from custom_errors import ElementError
from bar_helper import get_note_info, get_break_info, get_tuplet_info
from constants.music_code import *
from constants.notes import ADDITIONAL_FERMATA, ADDITIONAL_STACCATO, NOTE_SYM_A, NOTE_EXPLEN_LONG, NOTE_IDX_SYMBOL, NOTE_ACCIDENTAL_FLAT, NOTE_ACCIDENTAL_SHARP, NOTE_IDX_ACCIDENTAL, NOTE_IDX_OCTAVE_SHORT, NOTE_IDX_OCTAVE_LONG, DURATION_QUARTER, DURATION_THIRTYSECOND, BREAK_SYM, NOTE_ELM_EXPLEN_LONG, ADDITIONAL_SLUR_BEGIN, ADDITIONAL_SLUR_END

def note_to_music_code(note_element: str, slur_state: bool):
    try:
        note, duration_in_32nd, additionals, new_slur_state = get_note_info(note_element, slur_state)
    except ElementError:
        print('Error when converting a note to music code.')
        raise

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

    total_ticks = duration_in_32nd * TICKS_THIRTYSECOND
    if ADDITIONAL_FERMATA in additionals:
        total_ticks *= 2

    # Managing articulation
    ticks_played = round(total_ticks * (ARTICULATION_STACCATO if ADDITIONAL_STACCATO in additionals else ARTICULATION_REGULAR))

    # Slur always override previous articulation
    if new_slur_state:
        ticks_played = total_ticks

    ticks_break = total_ticks - ticks_played

    music_code = f"{ticks_played}{note_char}{octave}{ticks_break}"
    if ADDITIONAL_FERMATA in additionals:
        # Account the possibility of fermatas
        music_code = PREFIX_FERMATA + music_code

    return music_code, new_slur_state

def break_to_music_code(break_element: str):
    try:
        duration_in_32nd = get_break_info(break_element)
    except ElementError:
        print('Error when converting a break to music code.')
        raise

    total_ticks = duration_in_32nd * TICKS_THIRTYSECOND

    return f"{BREAK_SYM}{total_ticks}"

def tuplet_to_music_code(tuplet: str, slur_state: bool):
    try:
        definition, elements, actual_beat_count, final_slur_state = get_tuplet_info(tuplet, slur_state)
    except ElementError:
        print('Error when converting a tuplet to music code.')
        raise

    # Unpack definition
    grouping, no_regular_notes, regular_duration = definition

    total_ticks = PPQN * (DURATION_QUARTER // regular_duration) * no_regular_notes
    regular_duration32_ticks = total_ticks / grouping * regular_duration / DURATION_THIRTYSECOND

    accumulated_error = 0.0
    music_codes = []

    print(elements)
    elements_ticks = []
    for element_sym, duration_in_32nd, *other in elements:
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
        note_or_break, duration_in_32nd, *additionals = element
        if element_sym == BREAK_SYM:
            music_codes.append(f"{BREAK_SYM}{element_ticks}")
        else:
            # TODO: Refactor this somehow :(
            additionals = additionals[0]
            octave = note_or_break[NOTE_IDX_OCTAVE_SHORT]
            note_ascii_idx = NOTE_CHAR_START_IDX + (ord(note_or_break[NOTE_IDX_SYMBOL]) - ord(NOTE_SYM_A)) * NOTE_CHAR_OFFSET_SYM
            if len(note_or_break) == NOTE_EXPLEN_LONG:
                if note_or_break[NOTE_IDX_ACCIDENTAL] == NOTE_ACCIDENTAL_SHARP:
                    note_ascii_idx += NOTE_CHAR_OFFSET_SHARP
                else:
                    note_ascii_idx += NOTE_CHAR_OFFSET_FLAT

                octave = note_or_break[NOTE_IDX_OCTAVE_LONG]
            note_char = chr(note_ascii_idx)

            if ADDITIONAL_FERMATA in additionals:
                element_ticks *= 2

            if ADDITIONAL_SLUR_BEGIN in additionals:
                slur_state = True
            elif ADDITIONAL_SLUR_END in additionals:
                slur_state = False

            # Managing articulation
            ticks_played = round(element_ticks * (ARTICULATION_STACCATO if ADDITIONAL_STACCATO in additionals else ARTICULATION_REGULAR))

            if slur_state:
                ticks_played = element_ticks

            ticks_break = element_ticks - ticks_played

            music_code = f"{ticks_played}{note_char}{octave}{ticks_break}"
            if ADDITIONAL_FERMATA in additionals:
                music_code = PREFIX_FERMATA + music_code

            music_codes.append(music_code)

    return music_codes, final_slur_state