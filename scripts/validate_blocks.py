from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import  BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from constants.setting_fields import FIELD_SEP
from typing import IO
from validate_bar_content import *
from validate_setting_content import validate_setting_field

def validate_bar(bar: str):
    content = bar[1:-1] # Extract content
    elements = content.split(ELEMENT_SEP)

    for element in elements:
        # Empty note
        if element == '':
            return False
        # Tuplets
        elif element[-1] == TUPLET_CLOSE:
            if validate_tuplet(element) == False:
                return False
        # Breaks
        elif element[0] == BREAK_SYM:
            if validate_break_structure(element) == False:
                return False
        # Notes
        else:
            if validate_note_structure(element) == False:
                return False

    return True

def validate_setting_block(setting_block: str):
    content = setting_block[1:-1] # Extract content
    fields = content.split(FIELD_SEP)

    for field in fields:
        field_stripped = field.strip()
        if validate_setting_field(field_stripped) == False:
            return False

    return True

def validate_blocks(file: IO):
    result = True
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
                    result = False
                last_open_idx = None
    return result
