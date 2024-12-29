from constants.setting_fields import *
from constants.notes import VALID_DURATIONS

def validate_setting_field(setting_field: str):
    if setting_field.count(FIELD_SEP_VAL) != 1:
        return False

    field, value = setting_field.split(FIELD_SEP_VAL)

    if field == FIELD_BPM:
        return value.isnumeric() and int(value) >= BPM_MIN

    elif field == FIELD_SKIPBARS:
        return value.isnumeric() and int(value) > 0

    elif field == FIELD_TIMESIG:
        if value.count(FIELD_SEP_TIMESIG) != 1:
            return False

        top, bottom = value.split(FIELD_SEP_TIMESIG)

        is_top_valid = top.isnumeric() and int(top) > 0
        is_bottom_valid = bottom.isnumeric() and int(bottom) in VALID_DURATIONS

        return is_top_valid and is_bottom_valid

    return False
