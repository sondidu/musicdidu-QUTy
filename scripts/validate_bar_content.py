from constants.notes import *

def validate_note_structure(note_structure: str):
    parts = note_structure.split(NOTESTRUCT_SEP)

    if not len(parts) in VALID_NOTESTRUCT_LENS:
        return False

    note, duration = parts[:NOTESTRUCT_EXPLEN_SHORT]

    # Check accidental
    if len(note) == NOTESTRUCT_EXPLEN_LONG:
        is_accidental_valid = note[NOTE_IDX_ACCIDENTAL] in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP
        if not is_accidental_valid:
            return False

    # Check note symbol
    is_symbol_valid = note[NOTE_IDX_SYMBOL] in VALID_SYMS
    if not is_symbol_valid:
        return False

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_EXPLEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    is_octave_valid = octave.isnumeric() and NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX
    if not is_octave_valid:
        return False

    # Check duration
    if not duration.isnumeric() or not int(duration) in VALID_DURATIONS:
        return False

    # No additionals
    if len(parts) == NOTESTRUCT_EXPLEN_SHORT:
        return True

    # Check additionals
    additionals = parts[NOTESTRUCT_IDX_ADDITIONALS]
    all_additionals_unique = len(set(additionals)) == len(additionals)
    all_additionals_valid = all(additional in VALID_ADDITIONALS for additional in additionals)
    no_slur_overlap = not (ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals)
    return all_additionals_unique and all_additionals_valid and no_slur_overlap

def validate_break_structure(break_structure: str):
    parts = break_structure.split(BREAKSTRUCT_SEP)

    if len(parts) != BREAKSTRUCT_EXPLEN:
        return False

    break_char, duration = parts

    is_valid_break = break_char == BREAK_SYM
    is_valid_duration = duration.isnumeric() and int(duration) in VALID_DURATIONS
    return is_valid_break and is_valid_duration

def validate_tuplet(tuplet: str):
    if tuplet[-1] != TUPLET_CLOSE:
        return False

    # The '(' char is not found
    if (tuplet_open_idx := tuplet.find(TUPLET_OPEN)) == -1:
        return False

    # Validating tuplet definition
    tuplet_definition = tuplet[:tuplet_open_idx]
    definition_parts = tuplet_definition.split(TUPLET_SEP_DEF)

    if len(definition_parts) != TUPLET_EXPDEFS:
        return False

    if not all(definition.isnumeric() for definition in definition_parts):
        return False

    grouping, no_regular_notes, regular_duration = definition_parts
    if not int(regular_duration) in VALID_DURATIONS:
        return False

    # Validating individual notes in tuplet
    tuplet_notes = tuplet[tuplet_open_idx + 1:-1]
    notes_splitted = tuplet_notes.split(TUPLET_SEP_NOTE)
    return all(validate_note_structure(note_structure) for note_structure in notes_splitted)
