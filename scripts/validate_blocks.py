from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import  BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from custom_errors import FieldError, InvalidSheet
from typing import IO
from validate_bar_content import *
from validate_setting_content import validate_key_val, fields_to_dict

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
    content = setting_block.strip(SETTING_OPEN + SETTING_CLOSE)

    try:
        settings_dict = fields_to_dict(content)
    except FieldError:
        print("Failed to convert setting fields to dictionary.")
        return

    invalid_fields = []
    for key, val in settings_dict.items():
        try:
            validate_key_val(key, val)
        except FieldError as error:
            invalid_fields.append(error)

    return invalid_fields

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
                errors = []
                if line[last_open_idx] == BAR_OPEN:
                    errors = validate_bar(block)
                else:
                    errors = validate_setting_block(block)

                if len(errors) != 0:
                    errors_count += len(errors)
                    print(f"\t{block} at line {line_no} column {last_open_idx} block {block_no} errors:")
                    for error in errors:
                        print(f"\t\t{error}")

                last_open_idx = None

    if errors_count != 0:
        raise InvalidSheet(errors_count, "block content")
