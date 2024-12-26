from constants import NOTE_ACCIDENTAL_SHARP, NOTE_ACCIDENTAL_FLAT, \
                        NOTE_VALID_NOTES, NOTE_OCTAVE_MAX, NOTE_OCTAVE_MIN, \
                        NOTE_STRUCTURE_SEPARATOR, NOTE_VALID_DURATIONS, \
                        NOTE_VALID_STRUCTURE_LENGTHS, NOTE_VALID_ADDITIONALS

def validate_note_structure(note_structure: str):
    splitted = note_structure.split(NOTE_STRUCTURE_SEPARATOR)

    if not len(splitted) in NOTE_VALID_STRUCTURE_LENGTHS:
        return False

    note, duration = splitted[:2]

    if len(note) == 2:
        is_note_valid = note[0] in NOTE_VALID_NOTES
        is_octave_valid = note[1].isnumeric() and NOTE_OCTAVE_MIN <= int(note[1]) <= NOTE_OCTAVE_MAX
        if not is_note_valid or not is_octave_valid:
            return False
    else:
        is_note_valid = note[0] in NOTE_VALID_NOTES
        is_accidental_valid = note[1] in NOTE_ACCIDENTAL_FLAT + NOTE_ACCIDENTAL_SHARP
        is_octave_valid = note[2].isnumeric() and NOTE_OCTAVE_MIN <= int(note[2]) <= NOTE_OCTAVE_MAX
        if not is_note_valid or not is_accidental_valid or not is_octave_valid:
            return False

    if not duration.isnumeric() or not int(duration) in NOTE_VALID_DURATIONS:
        return False

    if len(splitted) == 2:
        return True

    additional = splitted[2]

    return additional in NOTE_VALID_ADDITIONALS
