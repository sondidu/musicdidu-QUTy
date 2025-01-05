from constants.notes import *
from custom_errors import BeatError, ElementError

duration_to_32nd = {
    1 : 32,
    2 : 16,
    4 : 8,
    8 : 4,
    16 : 2,
    32 : 1
}

def get_note_beats(note_element: str, is_in_slur: bool):
    parts = note_element.split(NOTESTRUCT_SEP)

    if not len(parts) in VALID_NOTESTRUCT_LENS:
        raise ElementError(note_element, f"unexpected number of parts '{NOTESTRUCT_SEP}'")

    note, duration = parts[:NOTESTRUCT_EXPLEN_SHORT]

    # Check accidental (sharp, flat, regular)
    if len(note) == NOTE_EXPLEN_LONG:
        accidental = note[NOTE_IDX_ACCIDENTAL]
        if not accidental in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP:
            raise ElementError(note_element, f"unknown accidental '{accidental}'")
    elif len(note) != NOTE_EXPLEN_SHORT:
        raise ElementError(note_element, f"unknown note '{note}'")

    # Check note symbol
    symbol = note[NOTE_IDX_SYMBOL]
    if symbol not in VALID_SYMS:
        raise ElementError(note_element, f"unknown symbol '{symbol}'")

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_EXPLEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    if not octave.isnumeric():
        raise ElementError(note_element, f"octave must be a number.")
    if not NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX:
        raise ElementError(note_element, f"octave must be between {NOTE_OCTAVE_MIN} and {NOTE_OCTAVE_MAX}")

    # Check duration
    try:
        duration_in_32nd = duration_to_32nd[int(duration)]
    except:
        raise ElementError(note_element, f"invalid duration '{duration}'")

    # No additionals
    if len(parts) == NOTESTRUCT_EXPLEN_SHORT:
        return duration_in_32nd, is_in_slur

    # Check additionals
    additionals = parts[NOTESTRUCT_IDX_ADDITIONALS]
    if len(set(additionals)) != len(additionals):
        raise ElementError(note_element, f"additionals '{additionals}' must all be unique")
    if not all(additional in VALID_ADDITIONALS for additional in additionals):
        raise ElementError(note_element, f"not all additionals '{additionals}' are valid")
    if ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals:
        raise ElementError(note_element, f"additionals '{additionals}' contain both '{ADDITIONAL_SLUR_BEGIN}' and '{ADDITIONAL_SLUR_END}'")

    if ADDITIONAL_SLUR_BEGIN in additionals:
        if is_in_slur:
            raise ElementError(note_element, f"currently in slur but found {ADDITIONAL_SLUR_BEGIN}")
        is_in_slur = True
    elif ADDITIONAL_SLUR_END in additionals:
        if not is_in_slur:
            raise ElementError(note_element, f"currently not in slur but found {ADDITIONAL_SLUR_END}")
        is_in_slur = False

    if ADDITIONAL_DOTNOTE in additionals:
        duration_in_32nd += duration_in_32nd // 2 # Add half its value

    return duration_in_32nd, is_in_slur

def get_break_beats(break_element: str):
    parts = break_element.split(BREAKSTRUCT_SEP)

    if len(parts) != BREAKSTRUCT_EXPLEN:
        raise ElementError(break_element, f"unexpected number of parts '{BREAKSTRUCT_SEP}'")

    break_char, duration = parts

    if break_char != BREAK_SYM:
        raise ElementError(break_element, "not a break element")

    try:
        duration_in_32nd = duration_to_32nd[int(duration)]
    except:
        raise ElementError(break_element, f"invalid duration '{duration}'")

    return duration_in_32nd


def get_tuplet_beats(tuplet: str, is_in_slur: bool):
    if tuplet[-1] != TUPLET_CLOSE:
        raise ElementError(tuplet, f"tuplet must end with a '{TUPLET_CLOSE}")

    # The '(' char is not found
    if (tuplet_open_idx := tuplet.find(TUPLET_OPEN)) == -1:
        raise ElementError(tuplet, f"tuplet must encapsulate notes with a '{TUPLET_OPEN}")

    # Validating tuplet definition
    tuplet_definition = tuplet[:tuplet_open_idx]
    definition_parts = tuplet_definition.split(TUPLET_SEP_DEF)

    if len(definition_parts) != TUPLET_EXPDEFS:
        raise ElementError(tuplet, f"unexpected number of definitions '{TUPLET_SEP_DEF}'")

    try:
        grouping, no_regular_notes, regular_duration = [int(definition_part) for definition_part in definition_parts]
    except:
        raise ElementError(tuplet, f"invalid tuplet definition(s) '{tuplet_definition}'")

    if grouping <= 0:
        raise ElementError(tuplet, f"grouping '{grouping}' must be greater than 0")

    if regular_duration <= 0:
        raise ElementError(tuplet, f"regular duration '{regular_duration}' must be greater than 0")

    if not regular_duration in VALID_DURATIONS:
        raise ElementError(tuplet, f"regular duration '{regular_duration}' is invalid")

    # Validating individual notes in tuplet
    expected_tuplet_beat_count = grouping * duration_to_32nd[regular_duration]
    actual_tuplet_beat_count = 0

    tuplet_elements = tuplet[tuplet_open_idx + 1:-1].split(TUPLET_SEP_NOTE)
    for tuplet_element in tuplet_elements:
        if tuplet_element[0] == BREAK_SYM:
            actual_tuplet_beat_count += get_break_beats(tuplet_element)
        else:
            beats_obtained, is_in_slur = get_note_beats(tuplet_element, is_in_slur)
            actual_tuplet_beat_count += beats_obtained

    if expected_tuplet_beat_count != actual_tuplet_beat_count:
        raise ElementError(tuplet, "tuplet beat count does not match")

    return no_regular_notes * duration_to_32nd[regular_duration], is_in_slur

def validate_bar_beats(actual_beat_count, tsig_top, tsig_bottom):
    try:
        expected_beat_count = tsig_top * duration_to_32nd[tsig_bottom]
    except:
        raise BeatError(msg="Top and bottom time signature values was never set.")

    if actual_beat_count != expected_beat_count:
        raise BeatError(expected_beat_count, actual_beat_count)
