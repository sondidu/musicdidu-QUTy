# consider renaming the file to bar_elements.py or something, but include 'element', maybe element_helpers?
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

def get_note_beats(note_element: str):
    parts = note_element.split(NOTESTRUCT_SEP)

    if not len(parts) in VALID_NOTESTRUCT_LENS:
        raise ElementError(note_element)

    note, duration = parts[:NOTESTRUCT_EXPLEN_SHORT]

    # Check accidental (sharp, flat, regular)
    if len(note) == NOTE_EXPLEN_LONG:
        if not note[NOTE_IDX_ACCIDENTAL] in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP:
            raise ElementError(note_element)
    elif len(note) != NOTE_EXPLEN_SHORT:
        raise ElementError(note_element)

    # Check note symbol
    if not note[NOTE_IDX_SYMBOL] in VALID_SYMS:
        raise ElementError(note_element)

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_EXPLEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    is_octave_valid = octave.isnumeric() and NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX
    if not is_octave_valid:
        raise ElementError(note_element)

    # Check duration
    try:
        duration_in_32nd = duration_to_32nd[int(duration)]
    except:
        raise ElementError(note_element)

    # No additionals
    if len(parts) == NOTESTRUCT_EXPLEN_SHORT:
        return duration_in_32nd

    # Check additionals
    additionals = parts[NOTESTRUCT_IDX_ADDITIONALS]
    all_additionals_unique = len(set(additionals)) == len(additionals)
    all_additionals_valid = all(additional in VALID_ADDITIONALS for additional in additionals)
    no_slur_overlap = not (ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals)
    if not (all_additionals_unique and all_additionals_valid and no_slur_overlap):
        raise ElementError(note_element)

    if ADDITIONAL_DOTNOTE in additionals:
        duration_in_32nd += duration_in_32nd // 2 # Add half its value

    return duration_in_32nd

def get_break_beats(break_element: str):
    parts = break_element.split(BREAKSTRUCT_SEP)

    if len(parts) != BREAKSTRUCT_EXPLEN:
        raise ElementError(break_element)

    break_char, duration = parts

    if break_char != BREAK_SYM:
        raise ElementError(break_element)

    try:
        duration_in_32nd = duration_to_32nd[int(duration)]
    except:
        raise ElementError(break_element)

    return duration_in_32nd


def get_tuplet_beats(tuplet: str):
    if tuplet[-1] != TUPLET_CLOSE:
        raise ElementError(tuplet)

    # The '(' char is not found
    if (tuplet_open_idx := tuplet.find(TUPLET_OPEN)) == -1:
        raise ElementError(tuplet)

    # Validating tuplet definition
    tuplet_definition = tuplet[:tuplet_open_idx]
    definition_parts = tuplet_definition.split(TUPLET_SEP_DEF)

    if len(definition_parts) != TUPLET_EXPDEFS:
        raise ElementError(tuplet)

    try:
        grouping, no_regular_notes, regular_duration = [int(definition_part) for definition_part in definition_parts]
    except:
        raise ElementError(tuplet)

    if grouping <= 0 or regular_duration <= 0:
        raise ElementError(tuplet)

    if not regular_duration in VALID_DURATIONS:
        raise ElementError(tuplet)

    # Validating individual notes in tuplet
    expected_tuplet_beat_count = grouping * duration_to_32nd[regular_duration]
    actual_tuplet_beat_count = 0

    tuplet_elements = tuplet[tuplet_open_idx + 1:-1].split(TUPLET_SEP_NOTE)
    for tuplet_element in tuplet_elements:
        if tuplet_element[0] == BREAK_SYM:
            actual_tuplet_beat_count += get_break_beats(tuplet_element)
        else:
            actual_tuplet_beat_count += get_note_beats(tuplet_element)

    if expected_tuplet_beat_count != actual_tuplet_beat_count:
        raise ElementError(tuplet)

    return no_regular_notes * duration_to_32nd[regular_duration]

def validate_bar_beats(actual_beat_count, tsig_top, tsig_bottom):
    try:
        expected_beat_count = tsig_top * duration_to_32nd[tsig_bottom]
    except:
        raise BeatError(msg="Top and bottom time signature values was never set.")

    if actual_beat_count != expected_beat_count:
        raise BeatError(expected_beat_count, actual_beat_count)

# validate_note_structure -> get_note_element_beats
# validate_break_structure -> get_break_element_beats
# validate_tuplet -> get_tuplet_beats, now also checks the count of each note element in the tuplet

# Each still only raises ElementError