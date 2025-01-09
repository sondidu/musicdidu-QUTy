from custom_errors import ElementError
from bar_helper import get_note_info, get_break_info
from constants.music_code import TICKS_THIRTYSECOND, ARTICULATION_REGULAR, ARTICULATION_STACCATO, NOTE_CHAR_START_IDX, NOTE_CHAR_OFFSET_SHARP, NOTE_CHAR_OFFSET_FLAT, NOTE_CHAR_OFFSET_SYM, PREFIX_FERMATA
from constants.notes import ADDITIONAL_FERMATA, ADDITIONAL_STACCATO, NOTE_SYM_A, NOTE_EXPLEN_LONG, NOTE_IDX_SYMBOL, NOTE_ACCIDENTAL_FLAT, NOTE_ACCIDENTAL_SHARP, NOTE_IDX_ACCIDENTAL, NOTE_IDX_OCTAVE_SHORT, NOTE_IDX_OCTAVE_LONG

def note_to_music_code(note_element: str, slur_state: bool):
    try:
        note, duration_in_32nd, additionals, new_slur_state = get_note_info(note_element, slur_state)
    except ElementError:
        print('Error when converting a note to music code.')
        raise

    total_ticks = duration_in_32nd * TICKS_THIRTYSECOND
    if ADDITIONAL_FERMATA in additionals:
        total_ticks *= 2

    # Managing articulation
    ticks_played = round(total_ticks * (ARTICULATION_STACCATO if ADDITIONAL_STACCATO in additionals else ARTICULATION_REGULAR))

    # Slur always override previous articulation
    if new_slur_state:
        ticks_played = total_ticks

    ticks_break = total_ticks - ticks_played

    # Getting note char and octave
    octave = note[NOTE_IDX_OCTAVE_SHORT]
    note_ascii_idx = NOTE_CHAR_START_IDX + (ord(note[NOTE_IDX_SYMBOL]) - ord(NOTE_SYM_A)) * NOTE_CHAR_OFFSET_SYM
    if len(note) == NOTE_EXPLEN_LONG:
        if note[NOTE_IDX_ACCIDENTAL] == NOTE_ACCIDENTAL_SHARP:
            note_ascii_idx += NOTE_CHAR_OFFSET_SHARP
        else:
            note_ascii_idx += NOTE_CHAR_OFFSET_FLAT

        octave = note[NOTE_IDX_OCTAVE_LONG]

    note_char = chr(note_ascii_idx)

    music_code = f"{ticks_played}{note_char}{octave}{ticks_break}"

    return music_code if ADDITIONAL_FERMATA not in additionals else f"{PREFIX_FERMATA}{music_code}", new_slur_state

def break_to_music_code(break_element: str):
    try:
        beats_in_32nd = get_break_info(break_element)
    except ElementError:
        print('Error when converting a break to music code.')
        raise

    return beats_in_32nd * TICKS_THIRTYSECOND

def tuplet_to_music_code(tuplet: str):
    pass