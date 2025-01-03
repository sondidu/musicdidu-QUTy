from constants.block_enclosures import BAR_CLOSE, BAR_OPEN, SETTING_CLOSE, SETTING_OPEN
from constants.notes import *
from constants.setting_fields import FIELD_TIMESIG, FIELD_SEP_TIMESIG, FIELD_SEP, FIELD_SEP_VAL
from typing import IO

duration_to_32nd = {
    1 : 32,
    2 : 16,
    4 : 8,
    8 : 4,
    16 : 2,
    32 : 1
}

def validate_bar_beats(bar: str, tsig_top: int, tsig_bottom: int):
    # Count every duration as 32nd notes
    expected_beat_count = tsig_top * duration_to_32nd[tsig_bottom]
    actual_beat_count = 0

    content = bar[1:-1] # Extract content

    elements = content.split(ELEMENT_SEP)

    for element in elements:
        # Ignore double (or multiple) (white)spaces
        if element == '':
            continue

        # Tuplet madness
        if element[-1] == TUPLET_CLOSE:
            tuplet_open_idx = element.find(TUPLET_OPEN)

            # Unpack definitions
            tuplet_definition = element[:tuplet_open_idx]
            definition_parts = [int(part) for part in tuplet_definition.split(TUPLET_SEP_DEF)] # Convert all definitions to ints
            grouping, no_regular_notes, regular_duration = definition_parts

            tuplet_note_structs_str = element[tuplet_open_idx + 1:-1]
            tuplet_note_structs = tuplet_note_structs_str.split(TUPLET_SEP_NOTE)

            expected_tuplet_count = grouping * duration_to_32nd[regular_duration]
            actual_tuplet_count = 0
            for tuplet_note_struct in tuplet_note_structs:
                # Unpack current tuplet note
                tuplet_note_parts = tuplet_note_struct.split(NOTESTRUCT_SEP)
                note, duration = tuplet_note_parts[:NOTE_EXPLEN_SHORT]
                additional = ''
                if len(tuplet_note_parts) == NOTE_EXPLEN_LONG:
                    additional = note_parts[NOTESTRUCT_IDX_ADDITIONALS]

                tuplet_note_count = duration_to_32nd[int(duration)]

                # Honestly, very rarely
                if ADDITIONAL_DOTNOTE in additional:
                    tuplet_note_count += tuplet_note_count // 2

                actual_tuplet_count += tuplet_note_count

            if actual_tuplet_count != expected_tuplet_count:
                return False

            actual_beats = no_regular_notes * duration_to_32nd[regular_duration] # To be added to `actual_beat_count`
            actual_beat_count += actual_beats

        else:
            # Note or break

            note_parts = element.split(NOTESTRUCT_SEP)

            note_or_break, duration = note_parts[:NOTE_EXPLEN_SHORT]
            additional = ''

            if len(note_parts) == NOTE_EXPLEN_LONG:
                additional = note_parts[NOTESTRUCT_IDX_ADDITIONALS]

            duration_in_32nds = duration_to_32nd[int(duration)]

            if ADDITIONAL_DOTNOTE in additional:
                duration_in_32nds += duration_in_32nds // 2 # Add half of its value

            actual_beat_count += duration_in_32nds

    return expected_beat_count == actual_beat_count

def validate_beats(file: IO):
    result = True
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
                        result = False

                last_open_idx = None
    return result
