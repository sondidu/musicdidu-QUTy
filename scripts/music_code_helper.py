from custom_errors import ElementError
from bar_helper import get_rest_info, get_note_info, get_tuplet_info
from constants.music_code import *
from constants.notes import *

def create_music_code_from_note(note: str, total_ticks: int, additionals: str, slur_state: bool):
    # Getting note char and octave
    note_ascii_dec = NOTE_CHAR_START_IDX + (ord(note[NOTE_IDX_SYMBOL]) - ord(NOTE_SYM_A)) * NOTE_CHAR_OFFSET_SYM
    if len(note) == NOTE_EXPLEN_LONG:
        if note[NOTE_IDX_ACCIDENTAL] == NOTE_ACCIDENTAL_SHARP:
            note_ascii_dec += NOTE_CHAR_OFFSET_SHARP
        else:
            note_ascii_dec += NOTE_CHAR_OFFSET_FLAT

        octave = note[NOTE_IDX_OCTAVE_LONG]
    else:
        octave = note[NOTE_IDX_OCTAVE_SHORT]
    note_char = chr(note_ascii_dec)

    # Account for fermatas
    if ADDITIONAL_FERMATA in additionals:
        total_ticks *= 2

    # Managing articulation
    if slur_state:
        # Slur always override previous articulation
        ticks_played = total_ticks
    else:
        ticks_played = round(total_ticks * (ARTICULATION_STACCATO if ADDITIONAL_STACCATO in additionals else ARTICULATION_REGULAR))

    ticks_rest = total_ticks - ticks_played

    music_code = f"{ticks_played}{note_char}{octave}{ticks_rest}"
    if ADDITIONAL_FERMATA in additionals:
        # Account for fermatas
        music_code = PREFIX_FERMATA + music_code

    return music_code

def note_to_music_code(note_element: str, slur_state: bool):
    try:
        note, duration_in_32nd, additionals, new_slur_state = get_note_info(note_element, slur_state)
    except ElementError:
        print('Error when converting a note to music code.')
        raise

    total_ticks = duration_in_32nd * TICKS_THIRTYSECOND
    music_code = create_music_code_from_note(note, total_ticks, additionals, new_slur_state)
    return music_code, new_slur_state, total_ticks

def rest_to_music_code(rest_element: str):
    try:
        duration_in_32nd = get_rest_info(rest_element)
    except ElementError:
        print('Error when converting a rest to music code.')
        raise

    total_ticks = duration_in_32nd * TICKS_THIRTYSECOND

    return f"{PREFIX_REST}{total_ticks}", total_ticks

def tuplet_to_music_codes(tuplet: str, slur_state: bool):
    try:
        definition, elements, actual_beat_count, final_slur_state = get_tuplet_info(tuplet, slur_state)
    except ElementError:
        print('Error when converting a tuplet to music code.')
        raise

    # Unpack definition
    grouping, no_regular_notes, regular_duration = definition

    total_ticks = int(PPQN * (DURATION_QUARTER / regular_duration) * no_regular_notes)
    regular_duration32_ticks = total_ticks / grouping * regular_duration / DURATION_THIRTYSECOND

    accumulated_error = 0.0
    music_codes = []

    elements_ticks = []
    for element_sym, duration_in_32nd, *other_info in elements:
        # Getting element's total ticks
        exact_duration = regular_duration32_ticks * duration_in_32nd
        accumulated_error += exact_duration - int(exact_duration)

        # Round up or down depending on accumulated error
        if accumulated_error >= 1.0:
            elements_ticks.append(int(exact_duration) + 1)
            accumulated_error -= 1.0
        else:
            elements_ticks.append(int(exact_duration))

    # At last element, add 1 if accumulated error's number is close to 1, else 0
    elements_ticks[-1] += round(accumulated_error)

    for element, element_ticks in zip(elements, elements_ticks):
        element_sym, *other_info = element
        if element_sym == REST_SYM:
            music_codes.append(f"{REST_SYM}{element_ticks}")
        else:
            duration_in_32nd, additionals = other_info

            # Manually check for slurs
            if ADDITIONAL_SLUR_END in additionals:
                slur_state = False
            elif ADDITIONAL_SLUR_BEGIN in additionals:
                slur_state = True

            music_code = create_music_code_from_note(element_sym, element_ticks, additionals, slur_state)
            music_codes.append(music_code)

    return music_codes, final_slur_state, total_ticks
