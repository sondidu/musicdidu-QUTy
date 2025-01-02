from constants.notes import  BREAK_SYM, ELEMENT_SEP, TUPLET_CLOSE
from constants.setting_fields import FIELD_SEP
from validate_bar_content import *
from validate_setting_content import validate_setting_field

def validate_bar(bar: str):
    content = bar[1:-1] # Extract content
    elements = content.split(ELEMENT_SEP)

    for element in elements:
        # Empty note
        if element == '':
            return False
        # Tuplets
        elif element[-1] == TUPLET_CLOSE:
            if validate_tuplet(element) == False:
                return False
        # Breaks
        elif element[0] == BREAK_SYM:
            if validate_break_structure(element) == False:
                return False
        # Notes
        else:
            if validate_note_structure(element) == False:
                return False

    return True

def validate_setting_block(setting_block: str):
    content = setting_block[1:-1] # Extract content
    fields = content.split(FIELD_SEP)

    for field in fields:
        field_stripped = field.strip()
        if validate_setting_field(field_stripped) == False:
            return False

    return True
