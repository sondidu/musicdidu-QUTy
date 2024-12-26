from constants.note import *

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
    is_octave_valid = octave.isnumeric() and OCTAVE_MIN <= int(octave) <= OCTAVE_MAX
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
    pass

def validate_bar(bar: str):
    pass

def validate_setting_block(setting_block: str):
    pass
