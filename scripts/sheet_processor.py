from bar_helper import get_bar_info
from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.setting_fields import KEY_ANACRUSIS, KEY_BPM, KEY_TIMESIG
from custom_errors import BeatError, BlockEnclosureError, ElementError, FieldError
from typing import TextIO
from setting_block_helper import get_setting_info

def process_sheet(file: TextIO):
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
