from generate_music_code import generate_music_code
from validate_sheet import validate_sheet
import os
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

validation_fail, validation_succeed = [], []
available_files = []

print('Validating Sheets'.center(50, '-'))
print()
for filename in os.listdir(sheets_dir):
    # Skip dirs and non-txt files
    if (os.path.isdir(filename) or not filename.endswith('.txt')):
        continue

    # Start validating
    with open(os.path.join(sheets_dir, filename), 'r') as sheet_file:
        print(f'Validating {filename}...')

        errors_or_sheet_info = validate_sheet(sheet_file)

        # Has errors
        if type(errors_or_sheet_info) == list:
            validation_fail.append(filename)

            print(f'{filename} errors:')
            for error in errors_or_sheet_info:
                print(error)
                print()
            continue

        # No errors
        validation_succeed.append(filename)

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

        # Generating music code file
        print()
        print(f"Generating music code for {filename}...")

        sheet_file.seek(0) # `process_sheet` iterates the entire file, thus need to reset pointer
        music_codes_per_line = generate_music_code(sheet_file)
        music_codes_per_line = [' '.join(music_codes) + '\n' for music_codes in music_codes_per_line]

        # Directory may not exist
        if not os.path.exists(music_code_dir):
            os.makedirs(music_code_dir)

        # Write music code to respective files in `music code/`
        output_music_code_path = os.path.join(music_code_dir, filename)
        with open(output_music_code_path, 'w') as music_code_file:
            music_code_file.writelines(music_codes_per_line)
            print(f'\t{output_music_code_path} successfully created!')
            print()

        # Add C file content
        var_name = filename[:-4].replace('.', '_') + '_music_code' # Account for multiple '.' and '.txt'
        music_code_content = ''.join(music_codes_per_line).replace('\n', '\\n')

        c_content_parts.append(f'const char {var_name}[] PROGMEM = "{music_code_content}";\n')
        available_files.append((f'{var_name}', var_name, f'sizeof({var_name})'))

print('Validation Summary'.center(50, '-'))

if validation_succeed:
    print('Succeed: ' + ', '.join(validation_succeed))

if validation_fail:
    print('Failed: ' + ', '.join(validation_fail))
    print()
    print('Some files still have errors.')
    print(f'{output_c_file} is not generated.')
    sys.exit(1)

c_content_parts.append('const FlashFile available_files[] = {\n')

for var_name, base_name, size in available_files:
    c_content_parts.append(f'    {{{var_name}, "{base_name}", {size}}},\n')

c_content_parts.append('};\n')
c_content_parts.append('const uint8_t available_files_count = sizeof(available_files) / sizeof(FlashFile);\n')

with open(output_c_file, 'w') as file:
    c_file_content = ''.join(c_content_parts)
    file.write(c_file_content)

print()
print(f'{output_c_file} is generated successfully.')