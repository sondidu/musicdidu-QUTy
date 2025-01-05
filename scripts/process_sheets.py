from custom_errors import InvalidSheet
from validate_beats import validate_beats
from validate_block_enclosures import validate_block_enclosures
from validate_blocks import validate_blocks
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

    # Validating sheets
    with open(os.path.join(sheets_dir, filename), 'r') as file:
        # Validate Enclosures
        print(f"Validating {filename}")
        print("Validating block enclosures...")
        try:
            validate_block_enclosures(file)
            print("\tNo errors regarding block enclosures.")
        except InvalidSheet as enclosure_error:
            print(enclosure_error)
            print()
            continue

        file.seek(0) # Because `validate_block_enclosures` iterates the entire file

        # Validate block content
        print("Validating block content...")
        try:
            validate_blocks(file)
            print("\tNo errors regarding block content.")
        except InvalidSheet as block_content:
            print(block_content)
            print()
            continue
        # add an except BlockError, refer to validate_blocks.py on why

        file.seek(0) # Because `validate_blocks` iterates the entire file
        continue

        # Validating beats
        overall_beats_check = validate_beats(file)
        if overall_beats_check == False:
            print("Not all bars have correct beats.")
            continue
        else:
            print("All bars have correct beats.")


c_file_content += 'const FlashFile available_files[] = {\n'

for var_name, base_name, size in available_files:
    c_file_content += f'    {{{var_name}, "{base_name}", {size}}},\n'

c_file_content += '};\n'
c_file_content += 'const uint8_t available_files_count = sizeof(available_files) / sizeof(FlashFile);\n'

with open(output_file, 'w') as file:
    file.write(c_file_content)

print(f'{output_file} generated successfully.')