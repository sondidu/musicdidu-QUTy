from constants.setting_fields import *
from constants.notes import VALID_DURATIONS

def validate_setting_field(setting_field: str):
    splitted = setting_field.split(SEPARATOR_VALUE)

    if len(splitted) != SPLITTED_FIELD_VALUE_LEN:
        return False

    field, value = splitted

    if field == FIELD_BPM:
        return value.isnumeric() and int(value) >= BPM_MIN

    elif field == FIELD_SKIP_BARS:
        return value.isnumeric() and int(value) > 0

    elif field == FIELD_TIME_SIGNATURE:
        time_signature_splitted = value.split(SEPARATOR_TIME_SIGNATURE)

        if len(time_signature_splitted) != SPLITTED_TIME_SIGNATURE_LEN:
            return False

        top, bottom = time_signature_splitted

        is_top_valid = top.isnumeric() and int(top) > 0
        is_bottom_valid = bottom.isnumeric() and int(bottom) in VALID_DURATIONS

        return is_top_valid and is_bottom_valid

    return False
