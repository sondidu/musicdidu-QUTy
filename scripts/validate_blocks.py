from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import  BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from constants.setting_fields import KEY_BPM, KEY_TIMESIG, SEP_FIELD
from custom_errors import BeatError, BlockEnclosureError, FieldError, InvalidSheet
from typing import IO
from bar_helper import *
from setting_block_helper import field_to_key_val

def validate_bar(bar: str, tsig_top: int, tsig_bottom: int, is_in_slur: bool):
    content = bar.strip(BAR_OPEN + BAR_CLOSE)
    elements = content.split(ELEMENT_SEP)

    beat_count = 0
    errors = []
    for element in elements:
        try:
            # Empty note
            if element == '':
                raise ElementError(element)
            # Tuplets
            elif element[-1] == TUPLET_CLOSE:
                beats_obtained, is_in_slur = get_tuplet_beats(element, is_in_slur)
                beat_count += beats_obtained
            # Breaks
            elif element[0] == BREAK_SYM:
                beat_count += get_break_beats(element)
            # Notes
            else:
                beats_obtained, is_in_slur = get_note_beats(element, is_in_slur)
                beat_count += beats_obtained
        except ElementError as error:
            errors.append(error)

    if len(errors) != 0:
        return errors

    try:
        validate_bar_beats(beat_count, tsig_top, tsig_bottom)
    except BeatError as error:
        errors.append(error)

    return is_in_slur

def setting_block_to_dict(setting_block: str):
    content = setting_block.strip(SETTING_OPEN + SETTING_CLOSE)

    fields = content.split(SEP_FIELD)
    fields = [field.strip() for field in fields]

    settings_dict = dict()
    invalid_fields = []
    for field in fields:
        try:
            key, val = field_to_key_val(field)
            if key in settings_dict:
                raise FieldError(field, f"Multiple instances of key '{key}'")
            settings_dict[key] = val
        except FieldError as error:
            invalid_fields.append(error)

    if len(invalid_fields) != 0:
        return invalid_fields

    return settings_dict

def validate_blocks(file: IO):
    errors_count = 0
    tsig_top = None
    tsig_bottom = None
    bpm = None
    is_in_slur = False
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
                try:
                    if line[last_open_idx] == BAR_OPEN and char == BAR_CLOSE:
                        if bpm is not None:
                            errors_or_new_slur_state = validate_bar(block, tsig_top, tsig_bottom, is_in_slur)
                            if type(errors_or_new_slur_state) == bool:
                                is_in_slur = errors_or_new_slur_state
                            else: # List contain errors
                                errors = errors_or_new_slur_state
                                errors.append("Fix all errors before beat count is checked.")
                        else:
                            raise BeatError(msg="BPM was never set.")
                    elif line[last_open_idx] == SETTING_OPEN and char == SETTING_CLOSE:
                        errors_or_settings_dict = setting_block_to_dict(block)

                        if type(errors_or_settings_dict) == dict:
                            if KEY_TIMESIG in errors_or_settings_dict:
                                tsig_top, tsig_bottom = errors_or_settings_dict[KEY_TIMESIG]
                            if KEY_BPM in errors_or_settings_dict:
                                bpm = errors_or_settings_dict[KEY_BPM]
                        else: # List contain errors
                            errors = errors_or_settings_dict
                    else:
                        raise BlockEnclosureError("Block enclosure error. THIS SHOULD NEVER HAPPEN", line_no, column_no)
                except Exception as error:
                    errors.append(error)

                if len(errors) != 0:
                    errors_count += len(errors)
                    print(f"\t{block} at line {line_no} column {last_open_idx} block {block_no} errors:")
                    for error in errors:
                        print(f"\t\t{error}")

                last_open_idx = None

    if errors_count != 0:
        raise InvalidSheet(errors_count, "block content")
