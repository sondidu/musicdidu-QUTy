from custom_errors import BlockEnclosureError
from sheet_processor import process_sheet
import os
import sys

sheets_dir = 'sheets'
output_file = 'src/data.c'

c_file_content = '''#include <avr/pgmspace.h>

#include "data.h"
#include "flash.h"

'''

# Build error if sheets/ is empty
if (len(os.listdir(sheets_dir)) == 0):
    print("There should be at least one .txt file in the sheets/ directory.")
    sys.exit(1)

available_files = []

print('-' * 10 + '\nProcessing Sheets' + '-' * 10)
for filename in os.listdir(sheets_dir):
    # Skip dirs and non-txt files
    if (os.path.isdir(filename) or not filename.endswith('.txt')):
        continue

    # Blindly adding everything
    # with open(os.path.join(sheets_dir, filename), 'r') as file:
    #     contents = file.read().replace('\n', '\\n')
    #     var_name = filename.replace('.', '_')[:-4] # Account for multiple '.'s and remove '.txt'
    #     c_file_content += f'const char {var_name}_contents[] PROGMEM = "{contents}";\n'
    #     available_files.append((f'{var_name}_contents', var_name, f'sizeof({var_name}_contents)'))

    with open(os.path.join(sheets_dir, filename), 'r') as file:
        print(f'Validating {filename}...')

        errors_or_sheet_info = process_sheet(file)

        # Has errors
        if type(errors_or_sheet_info) == list:
            print(f'{filename} errors:')
            for error in errors_or_sheet_info:
                print(error)
                print()
            continue

        # No errors
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

# c_file_content += 'const FlashFile available_files[] = {\n'

# for var_name, base_name, size in available_files:
#     c_file_content += f'    {{{var_name}, "{base_name}", {size}}},\n'

# c_file_content += '};\n'
# c_file_content += 'const uint8_t available_files_count = sizeof(available_files) / sizeof(FlashFile);\n'

# with open(output_file, 'w') as file:
#     file.write(c_file_content)

# print(f'{output_file} generated successfully.')