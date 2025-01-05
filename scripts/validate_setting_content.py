from constants.setting_fields import *
from custom_errors import FieldError

def validate_key_val(key: str, val: str):
    field = f"{key}={val}"
    incorrect_val_msg = f"{key}'s value is incorrect." # More detailed error messages in the future
    if key == KEY_BPM:
        if not val.isnumeric() or int(val) < BPM_MIN:
            raise FieldError(field, incorrect_val_msg)
    elif key == KEY_SKIPBARS:
        if not val.isnumeric() or int(val) <= 0:
            raise FieldError(field, incorrect_val_msg)
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
    elif key == KEY_ANACRUSIS:
        if val not in VALID_ANACRUSIS_VALUES:
            raise FieldError(field, incorrect_val_msg)
    else:
        raise FieldError(field, f"Invalid key '{key}'.")

def fields_to_dict(setting_fields: str):
    fields = setting_fields.split(SEP_FIELD)
    fields = [field.strip() for field in fields]

    result = dict()

    for field in fields:
        parts = field.split(SEP_KEYVAL)

        if len(parts) != EXPLEN_KEYVAL:
            raise FieldError(field)

        try:
            key, val = parts
        except:
            raise FieldError(field)

        if key in result:
            raise FieldError(field, f"The key '{key}' already exists.")

        result[key] = val

    return result
