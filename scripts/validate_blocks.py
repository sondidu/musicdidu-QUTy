from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import  BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from constants.setting_fields import FIELD_SEP
from custom_errors import ElementError, InvalidSheet
from typing import IO
from validate_bar_content import *
from validate_setting_content import validate_setting_field

def validate_bar(bar: str):
    content = bar[1:-1] # Extract content
    elements = content.split(ELEMENT_SEP)

    invalid_elements = []
    for element in elements:
        try:
            # Empty note
            if element == '':
                raise ElementError(element)
            # Tuplets
            elif element[-1] == TUPLET_CLOSE:
                validate_tuplet(element)
            # Breaks
            elif element[0] == BREAK_SYM:
                validate_break_structure(element)
            # Notes
            else:
                validate_note_structure(element)
        except ElementError as error:
            invalid_elements.append(error)

    return invalid_elements

def validate_setting_block(setting_block: str):
    content = setting_block[1:-1] # Extract content
    fields = content.split(FIELD_SEP)

    for field in fields:
        field_stripped = field.strip()
        if validate_setting_field(field_stripped) == False:
            return False

    return True

def validate_blocks(file: IO):
    errors_count = 0
    # TODO: Ensure that BPM and TIMESIG are already set before checking bars
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

                # Validate block
                if line[last_open_idx] == BAR_OPEN:
                    invalid_elements = validate_bar(block)
                    if len(invalid_elements) != 0:
                        print(f"\t{block} at line {line_no} column {last_open_idx} block {block_no} errors:")
                        for invalid_element in invalid_elements:
                            print(f"\t\t{invalid_element}")

                else:
                    validate_setting_block(block)
                last_open_idx = None

    if errors_count != 0:
        raise InvalidSheet(errors_count, "element syntax")
