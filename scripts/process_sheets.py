from validate_block_enclosures import validate_block_enclosures
from validate_blocks import validate_bar, validate_setting_block
from validate_beats import validate_bar_beats
from constants.block_enclosures import BAR_OPEN, BAR_CLOSE, SETTING_OPEN, SETTING_CLOSE
from constants.setting_fields import FIELD_TIMESIG, FIELD_SEP_TIMESIG, FIELD_SEP, FIELD_SEP_VAL
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
        block_enclosure_check = validate_block_enclosures(file)
        if block_enclosure_check == False:
            continue

        file.seek(0) # Because `validate_block_enclosures` iterates the entire file

        # Validate element syntax
        print("Validating element syntax...")
        element_syntax_check = True
        for line_no, line in enumerate(file, start=1):
            last_open_idx = None
            block_no = 0
            for column_no, char in enumerate(line):
                if char == BAR_OPEN or char == SETTING_OPEN:
                    last_open_idx = column_no
                elif char == BAR_CLOSE or char == SETTING_CLOSE:
                    # Extract block
                    block = line[last_open_idx:column_no + 1]

                    block_no += 1
                    block_check = False

                    # Validate block
                    if line[last_open_idx] == BAR_OPEN:
                        block_check = validate_bar(block)
                    else:
                        block_check = validate_setting_block(block)

                    if block_check == False:
                        print(f"Error at line {line_no} block no. {block_no} '{block}'.")
                        element_syntax_check = False
                    last_open_idx = None

        if element_syntax_check == False:
            print("Some errors in element syntax.")
            continue
        else:
            print("No errors in element syntax.")

        file.seek(0) # Because previously iterated entire file

        # Validating beats
        overall_beats_check = True
        curr_tsig_top = None
        curr_tsig_bottom = None
        for line_no, line in enumerate(file, start=1):
            last_open_idx = None
            block_no = 0
            for column_no, char in enumerate(line):
                if char == BAR_OPEN or char == SETTING_OPEN:
                    last_open_idx = column_no
                elif char == BAR_CLOSE or char == SETTING_CLOSE:
                    # Extract block
                    block = line[last_open_idx:column_no + 1]

                    block_no += 1

                    if line[last_open_idx] == SETTING_OPEN:
                        # Madness, will comment or make better later
                        if FIELD_TIMESIG in block:
                            field_tsig_idx_start = block.find(FIELD_TIMESIG)
                            next_sep = block[field_tsig_idx_start:].find(FIELD_SEP)
                            field_tsig_str = block[field_tsig_idx_start:-1].strip()
                            if next_sep != -1:
                                field_tsig_str = block[field_tsig_idx_start:next_sep]
                            tsig_top_str, tsig_bottom_str = field_tsig_str[field_tsig_str.find(FIELD_SEP_VAL) + 1:].split(FIELD_SEP_TIMESIG)
                            curr_tsig_top, curr_tsig_bottom = int(tsig_top_str), int(tsig_bottom_str)
                    else:
                        if curr_tsig_top == None or curr_tsig_bottom == None:
                            print("Time signature was never set.")
                            continue

                        beats_check = validate_bar_beats(block, curr_tsig_top, curr_tsig_bottom)
                        if beats_check == False:
                            print(f"Unmatch beats at line {line_no} block no. {block_no} '{block}'.")
                            overall_beats_check = False

                    last_open_idx = None

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