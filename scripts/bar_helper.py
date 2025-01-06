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

def get_note_info(note_element: str, is_in_slur: bool):
    parts = note_element.split(NOTESTRUCT_SEP)

    if not len(parts) in VALID_NOTESTRUCT_LENS:
        raise ElementError(note_element, f"Unexpected number of parts '{NOTESTRUCT_SEP}'")

    note, duration = parts[:NOTESTRUCT_EXPLEN_SHORT]

    # Check accidental (sharp, flat, regular)
    if len(note) == NOTE_EXPLEN_LONG:
        accidental = note[NOTE_IDX_ACCIDENTAL]
        if not accidental in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP:
            raise ElementError(note_element, f"Invalid accidental '{accidental}', valid accidentals are {NOTE_ACCIDENTAL_FLAT}{NOTE_ACCIDENTAL_SHARP}")
    elif len(note) != NOTE_EXPLEN_SHORT:
        raise ElementError(note_element, f"Invalid note '{note}'")

    # Check note symbol
    symbol = note[NOTE_IDX_SYMBOL]
    if symbol not in VALID_SYMBOLS:
        raise ElementError(note_element, f"Invalid symbol '{symbol}', valid symbols are {''.join(VALID_SYMBOLS)}")

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_EXPLEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    if not octave.isnumeric():
        raise ElementError(note_element, f"Octave '{octave}' must be a number")
    if not NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX:
        raise ElementError(note_element, f"Octave '{octave}' must be between {NOTE_OCTAVE_MIN} and {NOTE_OCTAVE_MAX}")

    # Check duration
    if not duration.isnumeric():
        raise ElementError(note_element, f"Duration '{duration}' must be a number")
    if int(duration) not in VALID_DURATIONS:
        raise ElementError(note_element, f"Duration '{duration}' must either be {', '.join(str(num) for num in VALID_DURATIONS)}")

    duration_in_32nd = duration_to_32nd[int(duration)]

    # No additionals
    if len(parts) == NOTESTRUCT_EXPLEN_SHORT:
        return duration_in_32nd, is_in_slur

    # Check additionals
    additionals = parts[NOTESTRUCT_IDX_ADDITIONALS]
    if len(set(additionals)) != len(additionals):
        raise ElementError(note_element, f"All additionals '{additionals}' must be unique")
    if not all(additional in VALID_ADDITIONALS for additional in additionals):
        raise ElementError(note_element, f"Not all additionals '{additionals}' are valid")
    if ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals:
        raise ElementError(note_element, f"Additionals '{additionals}' must not contain both '{ADDITIONAL_SLUR_BEGIN}' and '{ADDITIONAL_SLUR_END}'")

    if ADDITIONAL_SLUR_BEGIN in additionals:
        if is_in_slur:
            raise ElementError(note_element, f"Currently in slur but found {ADDITIONAL_SLUR_BEGIN}")
        is_in_slur = True
    elif ADDITIONAL_SLUR_END in additionals:
        if not is_in_slur:
            raise ElementError(note_element, f"Currently not in slur but found {ADDITIONAL_SLUR_END}")
        is_in_slur = False

    if ADDITIONAL_DOTNOTE in additionals:
        duration_in_32nd += duration_in_32nd // 2 # Add half its value

    return duration_in_32nd, is_in_slur

def get_break_info(break_element: str):
    parts = break_element.split(BREAKSTRUCT_SEP)

    if len(parts) != BREAKSTRUCT_EXPLEN:
        raise ElementError(break_element, f"Unexpected number of parts '{BREAKSTRUCT_SEP}'")

    break_char, duration = parts

    # Unlikely to happen
    if break_char != BREAK_SYM:
        raise ElementError(break_element, "Not a break element")

    # Check duration
    if not duration.isnumeric():
        raise ElementError(break_element, f"Duration must be a number")

    if int(duration) not in duration_to_32nd:
        raise ElementError(break_element, f"Duration must either be {', '.join(str(num) for num in VALID_DURATIONS)}")

    return duration_to_32nd[int(duration)]

def get_tuplet_info(tuplet: str, is_in_slur: bool):
    # Unlikely to happen
    if tuplet[-1] != TUPLET_CLOSE:
        raise ElementError(tuplet, f"Tuplet must end with a '{TUPLET_CLOSE}")

    # The TUPLET_OPEN aka '(' char is not found
    if (tuplet_open_idx := tuplet.find(TUPLET_OPEN)) == -1:
        raise ElementError(tuplet, f"Tuplet must encapsulate notes with a '{TUPLET_OPEN}")

    # Checking tuplet definition
    tuplet_definition = tuplet[:tuplet_open_idx]
    definition_parts = tuplet_definition.split(TUPLET_SEP_DEF)

    if len(definition_parts) != TUPLET_EXPDEFS:
        raise ElementError(tuplet, f"Unexpected number of definitions '{TUPLET_SEP_DEF}'")

    grouping, no_regular_notes, regular_duration = definition_parts

    if not grouping.isnumeric():
        raise ElementError(tuplet, f"Grouping '{grouping}' must be a number")

    if not no_regular_notes.isnumeric():
        raise ElementError(tuplet, f"Number of regular notes '{no_regular_notes}' must be a number")

    if not regular_duration.isnumeric():
        raise ElementError(tuplet, f"Regular duration '{regular_duration}' must be a number")

    grouping, no_regular_notes, regular_duration = int(grouping), int(no_regular_notes), int(regular_duration)

    if grouping <= 0:
        raise ElementError(tuplet, f"Grouping '{grouping}' must be greater than 0")

    if not regular_duration in VALID_DURATIONS:
        raise ElementError(tuplet, f"Regular duration '{regular_duration}' must either be {', '.join(str(num) for num in VALID_DURATIONS)}")


    # Validating individual notes in tuplet
    expected_tuplet_beat_count = grouping * duration_to_32nd[regular_duration]
    actual_tuplet_beat_count = 0

    tuplet_note_count, tuplet_break_count = 0, 0
    tuplet_elements = tuplet[tuplet_open_idx + 1:-1].split(TUPLET_SEP_NOTE)
    for tuplet_element in tuplet_elements:
        if tuplet_element[0] == BREAK_SYM:
            actual_tuplet_beat_count += get_break_info(tuplet_element)
            tuplet_break_count += 1
        else:
            beats_obtained, is_in_slur = get_note_info(tuplet_element, is_in_slur)
            actual_tuplet_beat_count += beats_obtained
            tuplet_note_count += 1

    if expected_tuplet_beat_count != actual_tuplet_beat_count:
        raise ElementError(tuplet, f"Expected {expected_tuplet_beat_count} tuplet beats (in 32nds) but got {actual_tuplet_beat_count}")

    actual_beat_count = no_regular_notes * duration_to_32nd[regular_duration]
    return actual_beat_count, is_in_slur, tuplet_note_count, tuplet_break_count

def validate_bar_beats(actual_beat_count: int, tsig_top: int, tsig_bottom: int):
    try:
        expected_beat_count = tsig_top * duration_to_32nd[tsig_bottom]
    except:
        raise BeatError(msg="Time signature was never set")

    if actual_beat_count != expected_beat_count:
        raise BeatError(expected_beat_count, actual_beat_count)
