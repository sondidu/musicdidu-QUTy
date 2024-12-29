from constants.notes import *

def validate_note_structure(note_structure: str):
    splitted = note_structure.split(SEPARATOR_NOTE_STRUCTURE)

    if not len(splitted) in VALID_STRUCTURE_LENGTHS:
        return False

    note, duration = splitted[:NOTE_STRUCTURE_LEN_SHORT]

    # Check accidental
    if len(note) == NOTE_STRUCTURE_LEN_LONG:
        is_accidental_valid = note[NOTE_IDX_ACCIDENTAL] in ACCIDENTAL_FLAT + ACCIDENTAL_SHARP
        if not is_accidental_valid:
            return False

    # Check note symbol
    is_symbol_valid = note[NOTE_IDX_SYMBOL] in VALID_SYMBOLS
    if not is_symbol_valid:
        return False

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_LEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    is_octave_valid = octave.isnumeric() and NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX
    if not is_octave_valid:
        return False

    # Check duration
    if not duration.isnumeric() or not int(duration) in VALID_DURATIONS:
        return False

    # No additionals
    if len(splitted) == NOTE_STRUCTURE_LEN_SHORT:
        return True

    # Check additionals
    additionals = splitted[NOTE_STRUCTURE_IDX_ADDITIONALS]
    all_additionals_unique = len(set(additionals)) == len(additionals)
    all_additionals_valid = all(additional in VALID_ADDITIONALS for additional in additionals)
    no_slur_overlap = not (ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals)
    return all_additionals_unique and all_additionals_valid and no_slur_overlap

def validate_break_structure(break_structure: str):
    splitted = break_structure.split(SEPARATOR_BREAK)

    if len(splitted) != BREAK_STRUCTURE_LEN:
        return False

    break_char, duration = splitted

    is_valid_break = break_char == SYMBOL_BREAK
    is_valid_duration = duration.isnumeric() and int(duration) in VALID_DURATIONS
    return is_valid_break and is_valid_duration

def validate_tuplet(tuplet: str):
    if tuplet.count(TUPLET_RATIO) != TUPLET_RATIO_COUNT_EXPECTED:
        return False

    if tuplet[-1] != TUPLET_CLOSE:
        return False

    # '(' not found
    if (tuplet_open_idx := tuplet.find(TUPLET_OPEN)) == -1:
        return False

    # Validating tuplet definition
    tuplet_defs = tuplet[:tuplet_open_idx]
    def_splitted = tuplet_defs.split(TUPLET_RATIO)

    if not all(tuplet_def.isnumeric() for tuplet_def in def_splitted):
        return False

    grouping, no_regular_notes, regular_duration = def_splitted
    if not int(regular_duration) in VALID_DURATIONS:
        return False

    # Validating individual notes in tuplet
    tuplet_notes = tuplet[tuplet_open_idx + 1:-1]
    notes_splitted = tuplet_notes.split(SEPARATOR_TUPLET_NOTE)
    return all(validate_note_structure(note_structure) for note_structure in notes_splitted)
