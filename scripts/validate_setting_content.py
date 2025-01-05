# consider renaming to setting_helpers
from constants.setting_fields import *
from custom_errors import FieldError

def field_to_key_val(field: str):
    field_parts = field.split(SEP_KEYVAL)

    if len(field_parts) != EXPLEN_KEYVAL:
        raise FieldError(field)

    key, val = field_parts
    incorrect_val_msg = f"{key}'s value is incorrect." # More detailed error messages in the future

    if key == KEY_BPM:
        if not val.isnumeric() or int(val) < BPM_MIN:
            raise FieldError(field, incorrect_val_msg)
        val = int(val)
    elif key == KEY_SKIPBARS:
        if not val.isnumeric() or int(val) <= 0:
            raise FieldError(field, incorrect_val_msg)
        val = int(val)
    elif key == KEY_TIMESIG:
        parts = val.split(SEP_VAL_TIMESIG)
        if len(parts) != EXPLEN_TIMESIG:
            raise FieldError(field, incorrect_val_msg)

        try:
            tsig_top, tsig_bottom = parts
        except:
            raise FieldError(field, incorrect_val_msg)

        if not tsig_top.isnumeric() or int(tsig_top) <= 0:
            raise FieldError(field, incorrect_val_msg)

        if not tsig_bottom.isnumeric() or int(tsig_bottom) not in VALID_TIMESIG_BOTTOM_VALUES:
            raise FieldError(field, incorrect_val_msg)

        val = (int(tsig_top), int(tsig_bottom))
    elif key == KEY_ANACRUSIS:
        if val not in VALID_ANACRUSIS_VALUES:
            raise FieldError(field, incorrect_val_msg)
    else:
        raise FieldError(field, f"Invalid key '{key}'.")

    return key, val
