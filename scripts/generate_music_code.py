from music_code_helper import rest_to_music_code,note_to_music_code, tuplet_to_music_codes
from constants.block_enclosures import *
from constants.setting_fields import ANACRUSIS_VAL_TRUE, KEY_ANACRUSIS, KEY_BPM, KEY_SKIPBARS, KEY_TIMESIG, SEP_VAL_TIMESIG, SEP_FIELD
from constants.music_code import PREFIX_ANACRUSIS, PREFIX_BPM, PREFIX_TIMESIG
from constants.notes import REST_SYM, ELEMENT_SEP, TUPLET_CLOSE
from setting_block_helper import field_to_key_val
from typing import TextIO

def bar_to_music_codes(bar_content: str, slur_state: bool):
    elements = bar_content.split(ELEMENT_SEP)

    music_codes = []
    bar_ticks = 0
    for element in elements:
        if element == '':
            continue

        if element[0] == REST_SYM:
            note_music_code, rest_ticks = rest_to_music_code(element)

            bar_ticks += rest_ticks
            music_codes.append(note_music_code)
        elif element[-1] == TUPLET_CLOSE:
            tuplet_music_codes, slur_state, note_ticks = tuplet_to_music_codes(element, slur_state)

            bar_ticks += note_ticks
            music_codes.extend(tuplet_music_codes) # Type is list hence use .extend()
        else:
            music_code, slur_state, tuplet_ticks = note_to_music_code(element, slur_state)

            bar_ticks += tuplet_ticks
            music_codes.append(music_code)

    return music_codes, slur_state, bar_ticks

def setting_block_to_music_codes(setting_block_content: str):
    fields = setting_block_content.split(SEP_FIELD)

    anacrusis = False
    skip_bars = 0

    music_codes = []
    for field in fields:
        field = field.replace(' ', '')

        key, val = field_to_key_val(field)

        if key == KEY_ANACRUSIS and val == ANACRUSIS_VAL_TRUE:
            anacrusis = True
        elif key == KEY_SKIPBARS:
            skip_bars = int(val)
        elif key == KEY_BPM:
            music_codes.append(f"{PREFIX_BPM}{val}")
        elif key == KEY_TIMESIG:
            tsig_top, tsig_bottom = val
            music_codes.append(f"{PREFIX_TIMESIG}{tsig_top}{SEP_VAL_TIMESIG}{tsig_bottom}")

    return music_codes, anacrusis, skip_bars

def generate_music_code(file: TextIO):
    slur_state = False
    is_anacrusis = False
    skip_bars = 0

    music_codes_per_line = []
    for line in file:
        # To make processing blocks easier
        line = line.strip('\n')
        line = line.replace(BAR_OPEN, '')
        line = line.replace(SETTING_OPEN, '')

        block_start_idx = 0
        music_codes = []
        for char_idx, char in enumerate(line):
            # Since open enclosures are stripped, only close enclosures are checked
            if char != BAR_CLOSE and char != SETTING_CLOSE:
                continue

            if char == BAR_CLOSE:
                # Processing bar

                bar = line[block_start_idx:char_idx] # Extract bar
                music_codes_from_bar, slur_state, bar_ticks = bar_to_music_codes(bar, slur_state)

                # Skip bars if needed
                if skip_bars > 0:
                    skip_bars -= 1
                    is_anacrusis = False # Overwrite anacrusis
                    block_start_idx = char_idx + 1 # Reset for next block
                    continue

                # Account anacrusis
                if is_anacrusis:
                    music_codes.append(f"{PREFIX_ANACRUSIS}{bar_ticks}")
                    is_anacrusis = False

                music_codes.extend(music_codes_from_bar)
            else:
                # Processing setting block

                setting_block = line[block_start_idx:char_idx] # Extract block
                music_codes_from_setting, is_anacrusis, skip_bars = setting_block_to_music_codes(setting_block)

                music_codes.extend(music_codes_from_setting)

            block_start_idx = char_idx + 1 # Current `char_idx` is the block's close, hence plus one

        if music_codes:
            music_codes_per_line.append(music_codes)

    return music_codes_per_line
