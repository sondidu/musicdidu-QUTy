from constants.notes import *
from custom_errors import ElementError

def validate_note_structure(note_structure: str):
    parts = note_structure.split(NOTESTRUCT_SEP)

    if not len(parts) in VALID_NOTESTRUCT_LENS:
        raise ElementError(note_structure)

    note, duration = parts[:NOTESTRUCT_EXPLEN_SHORT]

    # Check accidental (sharp, flat, regular)
    if len(note) == NOTE_EXPLEN_LONG:
        is_accidental_valid = note[NOTE_IDX_ACCIDENTAL] in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP
        if not is_accidental_valid:
            raise ElementError(note_structure)
    elif len(note) != NOTE_EXPLEN_SHORT:
        raise ElementError(note_structure)

    # Check note symbol
    is_symbol_valid = note[NOTE_IDX_SYMBOL] in VALID_SYMS
    if not is_symbol_valid:
        raise ElementError(note_structure)

    # Check octave
    octave = note[NOTE_IDX_OCTAVE_SHORT if len(note) == NOTE_EXPLEN_SHORT else NOTE_IDX_OCTAVE_LONG]
    is_octave_valid = octave.isnumeric() and NOTE_OCTAVE_MIN <= int(octave) <= NOTE_OCTAVE_MAX
    if not is_octave_valid:
        raise ElementError(note_structure)

    # Check duration
    if not duration.isnumeric() or not int(duration) in VALID_DURATIONS:
        raise ElementError(note_structure)

    # No additionals
    if len(parts) == NOTESTRUCT_EXPLEN_SHORT:
        return

    # Check additionals
    additionals = parts[NOTESTRUCT_IDX_ADDITIONALS]
    all_additionals_unique = len(set(additionals)) == len(additionals)
    all_additionals_valid = all(additional in VALID_ADDITIONALS for additional in additionals)
    no_slur_overlap = not (ADDITIONAL_SLUR_BEGIN in additionals and ADDITIONAL_SLUR_END in additionals)
    if not (all_additionals_unique and all_additionals_valid and no_slur_overlap):
        raise ElementError(note_structure)

def validate_break_structure(break_structure: str):
    parts = break_structure.split(BREAKSTRUCT_SEP)

    if len(parts) != BREAKSTRUCT_EXPLEN:
        raise ElementError(break_structure)

    break_char, duration = parts

    is_valid_break = break_char == BREAK_SYM
    is_valid_duration = duration.isnumeric() and int(duration) in VALID_DURATIONS
    if not (is_valid_break and is_valid_duration):
        raise ElementError(break_structure)

def validate_tuplet(tuplet: str):
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

    if not all(definition.isnumeric() for definition in definition_parts):
        raise ElementError(tuplet)

    grouping, no_regular_notes, regular_duration = definition_parts
    if not int(regular_duration) in VALID_DURATIONS:
        raise ElementError(tuplet)

    # Validating individual notes in tuplet
    tuplet_notes = tuplet[tuplet_open_idx + 1:-1]
    note_structures = tuplet_notes.split(TUPLET_SEP_NOTE)
    for note_structure in note_structures:
        validate_note_structure(note_structure)
