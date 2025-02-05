from generate_music_code import generate_music_code
from validate_sheet import validate_sheet
import os
import shutil
import sys

sheets_dir = 'sheets'
music_code_dir = 'music code'
output_c_file = os.path.join('src', 'data.c')

c_content_parts = ['''#include <avr/pgmspace.h>

#include "data.h"
#include "flash.h"

''']

# Build error if sheets/ is empty
if (len(os.listdir(sheets_dir)) == 0):
    print("There should be at least one .txt file in the sheets/ directory.")
    sys.exit(1)

# Prepare 'music code/' directory for new build
if os.path.exists(music_code_dir):
    shutil.rmtree(music_code_dir)
os.makedirs(music_code_dir)

files_failed, files_succeed = [], []
available_file_infos = [] # Store variable name, base name, size of each file

# Parse whitelist
whitelist_path = os.path.join(sheets_dir, 'whitelist')
whitelist_exists = os.path.exists(whitelist_path)
whitelist_files = []
if whitelist_exists:
    print('Whitelist file detected!')
    with open(whitelist_path, 'r') as whitelist_file:
        whitelist_files = [line.strip() for line in whitelist_file if line.strip()]

    # Build error if whitelist is empty
    if len(whitelist_files) == 0:
        print('There should be at least one filename in whitelist.')
        sys.exit(1)

    # Build error if none of filenames in whitelist exist in the actual directory
    available_files = [filename.removesuffix('.txt') for filename in os.listdir(sheets_dir)]
    available_files.remove('whitelist') # Remove whitelist itself
    if not (set(whitelist_files) & set(available_files)):
        print('There should be at least one filename in whitelist that matches in the sheets/ directory.')
        sys.exit(1)


# Begin validation
print('Validating Sheets'.center(50, '-'))
print()

for filename in sorted(os.listdir(sheets_dir)):
    # Skip dirs and non-txt files
    if (os.path.isdir(filename) or not filename.endswith('.txt')):
        continue

    # Skip if not in whitelist
    if whitelist_exists and filename.removesuffix('.txt') not in whitelist_files:
        continue

    # Start validating
    with open(os.path.join(sheets_dir, filename), 'r') as sheet_file:
        print(f'Validating {filename}...')

        errors_or_sheet_info = validate_sheet(sheet_file)

        # Has errors
        if type(errors_or_sheet_info) == list:
            files_failed.append(filename)

            print(f'{filename} errors:')
            for error in errors_or_sheet_info:
                print(error)
                print()
            continue

        # No errors
        files_succeed.append(filename)

        # Unpack and print
        block_count, bar_count, setting_count, beat_count, \
            element_count, note_count, break_count = errors_or_sheet_info

        print(f"Validating {filename} is complete! Here are its info:")
        print(f"- Block count: {block_count}")
        print(f"   - Bar count: {bar_count}")
        print(f"   - Setting Block count: {setting_count}")
        print(f"- Total beats: {beat_count}")
        print(f"- Total elements: {element_count}")
        print(f"   - Total notes: {note_count}")
        print(f"   - Total breaks: {break_count}")
        print()

        # Generating music code file
        # print()
        # print(f"Generating music code for {filename}...")

        sheet_file.seek(0) # `process_sheet` iterates the entire file, thus need to reset pointer
        music_codes_per_line = generate_music_code(sheet_file)

        # Converting to one big music code separated with newlines and spaces
        music_codes_per_line = [' '.join(music_codes) for music_codes in music_codes_per_line]
        music_codes_per_line = '\n'.join(music_codes_per_line)

        # Write music code to respective file in `music code/`
        output_music_code_path = os.path.join(music_code_dir, filename)
        with open(output_music_code_path, 'w') as music_code_file:
            music_code_file.writelines(music_codes_per_line)
            # print(f'\t{output_music_code_path} successfully created!')
            # print()

        # Add C file content
        var_name = filename[:-4].replace('.', '_') + '_music_code' # Account for multiple '.' and '.txt'
        music_code_content = ''.join(music_codes_per_line).replace('\n', '\\n')

        c_content_parts.append(f'const char {var_name}[] PROGMEM = "{music_code_content}";\n')
        available_file_infos.append((f'{var_name}', var_name, f'sizeof({var_name})'))

# Print validation summary
print('Validation Summary'.center(50, '-'))

if files_succeed and len(files_failed) == 0:
    print('All sheet(s) successfully validated:')
    for file_num, filename in enumerate(files_succeed, start=1):
        print(f"{file_num}. {filename}")
    print(f'See the `{music_code_dir}` directory to see their respective music codes.')

if files_failed:
    print('Failed sheet(s):')
    for file_num, filename in enumerate(files_failed, start=1):
        print(f"{file_num}. {filename}")

    print()
    print('Some files still have errors.')
    print(f'{output_c_file} is not generated.')
    sys.exit(1)

# Append rest of C file content
c_content_parts.append('const FlashFile available_files[] = {\n')

for var_name, base_name, size in available_file_infos:
    c_content_parts.append(f'    {{{var_name}, "{base_name}", {size}}},\n')

c_content_parts.append('};\n')
c_content_parts.append('const uint8_t available_files_count = sizeof(available_files) / sizeof(FlashFile);\n')

# Write file
with open(output_c_file, 'w') as file:
    c_file_content = ''.join(c_content_parts)
    file.write(c_file_content)

print()
print(f'{output_c_file} is generated successfully.')
print()