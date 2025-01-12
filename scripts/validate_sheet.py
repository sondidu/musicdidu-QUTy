from bar_helper import get_break_info, get_note_info, get_tuplet_info, validate_bar_beats
from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from constants.setting_fields import KEY_ANACRUSIS, KEY_BPM, KEY_TIMESIG, SEP_FIELD
from custom_errors import BeatError, BlockEnclosureError, ElementError, FieldError
from typing import TextIO
from setting_block_helper import field_to_key_val

def split_with_indices(s: str, sep=' '):
    parts = s.split(sep)
    res = [(0, parts[0])]

    for i in range(1, len(parts)):
        idx, word = res[i - 1]
        res.append((idx + len(word) + len(sep), parts[i]))

    return res

def get_setting_info(setting_block: str, line_no=0, line_content='', setting_start_idx=0):
    content = setting_block.strip(SETTING_OPEN + SETTING_CLOSE)
    fields = split_with_indices(content, SEP_FIELD)

    settings_dict = dict()
    errors = []
    for idx, field in fields:
        field_stripped = field.strip()
        try:
            key, val = field_to_key_val(field_stripped)
            if key in settings_dict:
                raise FieldError(field, f"Multiple instances of key '{key}'")
            settings_dict[key] = val
        except FieldError as error:
            first_line = f"{line_content} at line {line_no}\n"
            no_of_spaces = setting_start_idx + idx + len(field) - len(field_stripped) + 1 # Account the open enclosure and potential whitespaces in fields
            pointer = no_of_spaces * ' ' + '^'

            constructed_msg = first_line + pointer + ' ' + str(error)
            errors.append(constructed_msg)


    if len(errors) != 0:
        return errors

    return settings_dict

def get_bar_info(bar: str, tsig_top: int, tsig_bottom: int, slur_state: bool, anacrusis=False, line_no=0, line_content='', bar_start_idx=0):
    content = bar.strip(BAR_OPEN + BAR_CLOSE)
    elements = split_with_indices(content, ELEMENT_SEP)

    beat_count, note_count, break_count = 0, 0, 0
    errors = []
    for idx, element in elements:
        try:
            # Empty note
            if element == '':
                raise ElementError(element, "No empty element (possibly double spaces)")
            # Tuplets
            elif element[-1] == TUPLET_CLOSE:
                tuplet_definition, tuplet_elements, beats_obtained, slur_state = get_tuplet_info(element, slur_state)

                # Count notes and breaks
                for symbol, *other_element_info in tuplet_elements:
                    if symbol == BREAK_SYM:
                        break_count += 1
                    else:
                        note_count += 1

                beat_count += beats_obtained

            # Breaks
            elif element[0] == BREAK_SYM:
                beat_count += get_break_info(element)
                break_count += 1
            # Notes
            else:
                note, beats_obtained, additionals, slur_state = get_note_info(element, slur_state)
                beat_count += beats_obtained
                note_count += 1
        except ElementError as error:
            first_line = f"{line_content} at line {line_no}\n"
            pointer = (bar_start_idx + idx + 1) * ' ' + '^' # The plus one is to account the open enclosure

            constructed_msg = first_line + pointer + ' ' + str(error)
            errors.append(constructed_msg)

    if len(errors) != 0:
        return errors

    try:
        if not anacrusis:
            validate_bar_beats(beat_count, tsig_top, tsig_bottom)
    except BeatError as error:
        first_line = f"{line_content} at line {line_no}\n"
        pointer = '^'
        constructed_msg = first_line + pointer + ' ' + str(error)
        return [constructed_msg]

    return slur_state, beat_count, len(elements), note_count, break_count

def validate_sheet(file: TextIO):
    open_enclosure_pairs = {
        BAR_OPEN : BAR_CLOSE,
        SETTING_OPEN : SETTING_CLOSE,
    }

    errors = []
    bar_count = 0
    setting_count = 0
    beat_count = 0
    element_count = 0
    note_count = 0
    break_count = 0

    tsig_top = None
    tsig_bottom = None
    bpm = None
    anacrusis = False
    slur_state = False

    for line_no, line in enumerate(file, start=1):
        open_enclosure_idx = None
        line = line.strip('\n')

        unknown_identifier_start_idx = None
        for char_idx, char in enumerate(line):
            # Always ignore whitespace
            if char.isspace():
                continue

            # Currently closed
            if open_enclosure_idx is None:
                if char not in open_enclosure_pairs:
                    # Encounter char that's not unknown
                    unknown_identifier_start_idx = char_idx if unknown_identifier_start_idx is None else unknown_identifier_start_idx
                else:
                    # Encounter char that's an opening enclosure '[' or '{'
                    open_enclosure_idx = char_idx

                    # Have previously marked an unknown identifier
                    if unknown_identifier_start_idx is not None:
                        errors.append(BlockEnclosureError(f"Unknown identifier '{line[unknown_identifier_start_idx:char_idx]}'", line_no, unknown_identifier_start_idx, line))
                        unknown_identifier_start_idx = None

                continue

            # Currently open

            # Checks for matching pair
            open_enclosure_char = line[open_enclosure_idx]
            if char != open_enclosure_pairs.get(open_enclosure_char):
                continue

            # Found matching enclosure pair
            block = line[open_enclosure_idx:char_idx + 1] # Extract block

            if open_enclosure_char == BAR_OPEN and char == BAR_CLOSE:
                # Process bar

                if bpm is None:
                    errors.append(BeatError(msg="BPM was never set."))
                    return errors

                if tsig_top is None or tsig_bottom is None:
                    errors.append(BeatError(msg="Time signature was never set."))
                    return errors

                bar = block
                bar_info_or_errors = get_bar_info(bar, tsig_top, tsig_bottom, slur_state, anacrusis, line_no, line, open_enclosure_idx)
                anacrusis = False # It's possible that this was True, hence set to False afterwards
                bar_count += 1

                if type(bar_info_or_errors) == list:
                    # Errors
                    errors.extend(bar_info_or_errors)
                else:
                    # Unpacking bar info
                    new_slur_state, beats_accumulated, elements_accumulated, notes_accumulated, breaks_accumulated = bar_info_or_errors

                    # Update relevant info
                    slur_state = new_slur_state
                    beat_count += beats_accumulated
                    element_count += elements_accumulated
                    note_count += notes_accumulated
                    break_count += breaks_accumulated
            else:
                # Process setting block

                setting_block = block
                setting_info_or_errors = get_setting_info(setting_block, line_no, line, open_enclosure_idx)
                setting_count += 1

                if type(setting_info_or_errors) == list:
                    # Errors
                    errors.extend(setting_info_or_errors)
                else:
                    # A dict of keys and values
                    if KEY_TIMESIG in setting_info_or_errors:
                        tsig_top, tsig_bottom = setting_info_or_errors[KEY_TIMESIG]
                    if KEY_BPM in setting_info_or_errors:
                        bpm = setting_info_or_errors[KEY_BPM]
                    if KEY_ANACRUSIS in setting_info_or_errors:
                        if setting_info_or_errors[KEY_ANACRUSIS] == "True":
                            anacrusis = True

            open_enclosure_idx = None # Prepare for next block

        if unknown_identifier_start_idx is not None:
            errors.append(BlockEnclosureError(f"Unknown identifier '{line[unknown_identifier_start_idx:]}'", line_no, unknown_identifier_start_idx, line))


        if open_enclosure_idx is not None:
            errors.append(BlockEnclosureError(f"Block was opened but never closed", line_no, open_enclosure_idx, line))

    if len(errors) != 0:
        return errors

    block_count = bar_count + setting_count
    return block_count, bar_count, setting_count, beat_count, element_count, note_count, break_count
