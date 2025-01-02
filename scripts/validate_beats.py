from constants.notes import ADDITIONAL_DOTNOTE, ELEMENT_SEP, NOTE_EXPLEN_SHORT, \
                            NOTE_EXPLEN_LONG, NOTESTRUCT_IDX_ADDITIONALS, NOTESTRUCT_SEP

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

        splitted = element.split(NOTESTRUCT_SEP)

        note, duration = splitted[:NOTE_EXPLEN_SHORT]
        additional = ''

        if len(splitted) == NOTE_EXPLEN_LONG:
            additional = splitted[NOTESTRUCT_IDX_ADDITIONALS]

        duration_in_32nds = duration_to_32nd[int(duration)]

        if ADDITIONAL_DOTNOTE in additional:
            duration_in_32nds += duration_in_32nds // 2 # Add half of its value

        actual_beat_count += duration_in_32nds

    return expected_beat_count == actual_beat_count
