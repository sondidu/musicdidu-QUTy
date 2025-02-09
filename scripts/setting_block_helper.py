from constants.music_code import FREQ_CLK_DIV2, PPQN # For BPM validation
from constants.setting_fields import *
from custom_errors import FieldError

def field_to_key_val(field: str):
    field_parts = field.split(SEP_KEYVAL)

    if len(field_parts) != EXPLEN_KEYVAL:
        raise FieldError(field)

    key, val = field_parts

    if key == KEY_BPM:
        parts = val.split(SEP_VAL_BPM)

        if len(parts) != EXPLEN_BPM:
            raise FieldError(field, f"Invalid BPM '{val}', the format is BPM_value/beat_value")

        bpm_value, beat_value = parts

        if not bpm_value.isnumeric():
            raise FieldError(field, "BPM Value must be an integer.")

        dotted_note_idx = beat_value.find(BPM_VAL_BEAT_VALUE_DOTTED_NOTE)

        # Handling both if '.' is present or not
        beat_value_without_dot = beat_value if dotted_note_idx == -1 else beat_value[:dotted_note_idx]
        if not beat_value_without_dot.isnumeric():
            raise FieldError(field, f"Beat Value must either be {', '.join(str(num) for num in VALID_BPM_BEAT_VALUES)} optionally followed by a '{BPM_VAL_BEAT_VALUE_DOTTED_NOTE}'")

        if dotted_note_idx != -1 and beat_value[dotted_note_idx:] != BPM_VAL_BEAT_VALUE_DOTTED_NOTE:
            raise FieldError(field, f"Dotted note must be '{BPM_VAL_BEAT_VALUE_DOTTED_NOTE}'")

        # Handling if the two values are valid
        beat_value_without_dot = int(beat_value_without_dot)
        actual_beat_value = beat_value_without_dot if dotted_note_idx == -1 else beat_value_without_dot + beat_value_without_dot // 2
        bpm_in_quarter_note = int(4 / actual_beat_value * int(bpm_value))
        bpm_period = FREQ_CLK_DIV2 * 60 // bpm_in_quarter_note // PPQN
        if bpm_period > 2**16 - 1:
            raise FieldError(field, f"Invalid BPM and Beat values '{bpm_value}/{beat_value}'. Please try a different value-pair")

        val = bpm_period
    elif key == KEY_SKIPBARS:
        if not val.isnumeric():
            raise FieldError(field, f"Number of bars skipped must be a number")

        if int(val) <= 0:
            raise FieldError(field, "Number of bars skipped must be greater than 0")

        val = int(val)
    elif key == KEY_TIMESIG:
        parts = val.split(SEP_VAL_TIMESIG)

        if len(parts) != EXPLEN_TIMESIG:
            raise FieldError(field, f"Invalid time signature '{val}', the format is top/bottom")

        tsig_top, tsig_bottom = parts

        if not tsig_top.isnumeric():
            raise FieldError(field, f"Time signature's top value must be a number")

        if int(tsig_top) <= 0:
            raise FieldError(field, "Time signature's top value must be greater than 0")

        if not tsig_bottom.isnumeric():
            raise FieldError(field, "Time signatures' bottom value must be a number")

        if int(tsig_bottom) not in VALID_TIMESIG_BOTTOM_VALUES:
            raise FieldError(field, f"Time signature's bottom value must either be {', '.join(str(num) for num in VALID_TIMESIG_BOTTOM_VALUES)}")

        val = (int(tsig_top), int(tsig_bottom))
    elif key == KEY_ANACRUSIS:
        if val not in VALID_ANACRUSIS_VALUES:
            raise FieldError(field, f"Anacrusis' value must either be {' or '.join(VALID_ANACRUSIS_VALUES)}")
    else:
        raise FieldError(field, f"Invalid key '{key}', valid keys are {', '.join(VALID_KEYS)}")

    return key, val
