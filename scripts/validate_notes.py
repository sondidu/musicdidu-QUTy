from constants.note import *

def validate_note_structure(note_structure: str):
    splitted = note_structure.split(STRUCTURE_SEPARATOR)

    if not len(splitted) in VALID_STRUCTURE_LENGTHS:
        return False

    note, duration = splitted[:2]

    if len(note) == 2:
        is_note_valid = note[0] in VALID_NOTES
        is_octave_valid = note[1].isnumeric() and OCTAVE_MIN <= int(note[1]) <= OCTAVE_MAX
        if not is_note_valid or not is_octave_valid:
            return False
    else:
        is_note_valid = note[0] in VALID_NOTES
        is_accidental_valid = note[1] in ACCIDENTAL_FLAT + ACCIDENTAL_SHARP
        is_octave_valid = note[2].isnumeric() and OCTAVE_MIN <= int(note[2]) <= OCTAVE_MAX
        if not is_note_valid or not is_accidental_valid or not is_octave_valid:
            return False

    if not duration.isnumeric() or not int(duration) in VALID_DURATIONS:
        return False

    if len(splitted) == 2:
        return True

    additional = splitted[2]

    return additional in VALID_ADDITIONALS
