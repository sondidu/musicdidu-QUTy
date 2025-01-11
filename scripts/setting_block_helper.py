from constants.block_enclosures import SETTING_CLOSE, SETTING_OPEN
from constants.setting_fields import *
from custom_errors import FieldError
from utils import split_with_indices

def field_to_key_val(field: str):
    field_parts = field.split(SEP_KEYVAL)

    if len(field_parts) != EXPLEN_KEYVAL:
        raise FieldError(field)

    key, val = field_parts

    if key == KEY_BPM:
        if not val.isnumeric():
            raise FieldError(field, f"Invalid value '{val}'")

        if int(val) < BPM_MIN:
            raise FieldError(field, f"BPM value must be greater than or equal to {BPM_MIN}")

        val = int(val)
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

def get_setting_info(setting_block: str, line_no=0, line_content='', setting_start_idx=0):
    content = setting_block.strip(SETTING_OPEN + SETTING_CLOSE)
    fields = split_with_indices(content, SEP_FIELD)

    settings_dict = dict()
    errors = []
    for idx, field in fields:
        field_stripped = field.strip()
        try:
            key, val = field_to_key_val(field_stripped)
            if key in settings_dict:
                raise FieldError(field, f"Multiple instances of key '{key}'")
            settings_dict[key] = val
        except FieldError as error:
            first_line = f"{line_content} at line {line_no}\n"
            no_of_spaces = setting_start_idx + idx + len(field) - len(field_stripped) + 1 # Account the open enclosure and potential whitespaces in fields
            pointer = no_of_spaces * ' ' + '^'

            constructed_msg = first_line + pointer + ' ' + str(error)
            errors.append(constructed_msg)


    if len(errors) != 0:
        return errors

    return settings_dict