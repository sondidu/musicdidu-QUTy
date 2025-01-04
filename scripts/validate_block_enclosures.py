from custom_errors import BlockError, InvalidSheet
from constants.block_enclosures import *
from typing import IO

def validate_block_enclosures(file: IO):
    bar_chars = set((BAR_OPEN, BAR_CLOSE))
    setting_chars = set((SETTING_OPEN, SETTING_CLOSE))
    block_chars = bar_chars | setting_chars
    errors_count = 0

    for line_no, line in enumerate(file, start=1):
        line = line[:-1] # Remove '\n' at the very end

        bar_opened_idx = None
        setting_opened_idx = None

        try:
            for column_no, char in enumerate(line):
                # Skip non-block chars
                if not char in block_chars:

                    # Mark non-block char if no block has been opened, ignore if whitespace
                    if bar_opened_idx == setting_opened_idx == None and not char.isspace():

                        # Find next non-block char
                        next_nonblock_idx = len(line)
                        for block_char_no, block_char in enumerate(line[column_no:]):
                            if block_char in block_chars:
                                next_nonblock_idx = block_char_no
                                break

                        nonblock_str = line[column_no:next_nonblock_idx]
                        raise BlockError(f"Non-block string '{nonblock_str}'", line_no, column_no)

                    continue

                if bar_opened_idx == None and setting_opened_idx == None:
                    if char == BAR_OPEN:
                        bar_opened_idx = column_no
                    if char == BAR_CLOSE:
                        raise BlockError(f"Bar was closed '{BAR_CLOSE}' but was never opened,", line_no, column_no)

                    if char == SETTING_OPEN:
                        setting_opened_idx = column_no
                    if char == SETTING_CLOSE:
                        raise BlockError(f"Setting block was closed '{SETTING_CLOSE}' but was never opened,", line_no, column_no)

                elif bar_opened_idx != None:
                    unallowed_chars = block_chars - {BAR_CLOSE}
                    if char in unallowed_chars:
                        raise BlockError(f"Bar '{BAR_OPEN}' is still opened at column {bar_opened_idx} but '{char}' was found,", line_no, column_no)
                    else:
                        current_bar = line[bar_opened_idx:column_no + 1]
                        content_within = current_bar[1:-1].strip()
                        if content_within == '':
                            raise BlockError(f"Empty bar '{current_bar}'", line_no, bar_opened_idx)
                        bar_opened_idx = None # Bar closed

                elif setting_opened_idx != None:
                    unallowed_chars = block_chars - {SETTING_CLOSE}
                    if char in unallowed_chars:
                        raise BlockError(f"Setting block '{SETTING_OPEN}' is still opened at column {setting_opened_idx} but '{char}' was found,", line_no, column_no)
                    else:
                        current_setting_block = line[setting_opened_idx:column_no + 1]
                        content_within = current_setting_block[1:-1].strip()
                        if content_within == '':
                            raise BlockError(f"Empty setting block '{current_setting_block}'", line_no, setting_opened_idx)
                        setting_opened_idx = None # Setting closed

            if bar_opened_idx != None:
                raise BlockError(f"Bar was opened '{BAR_OPEN}' at column {bar_opened_idx} but never closed '{BAR_CLOSE}'.", line_no, len(line))
            if setting_opened_idx != None:
                raise BlockError(f"Setting block was opened '{SETTING_OPEN}' at column {setting_opened_idx} but never closed '{BAR_CLOSE}'.", line_no, len(line))

        except BlockError as error:
            errors_count += 1
            print(error)


    if errors_count != 0:
        raise InvalidSheet(f"There are {errors_count} errors regarding block enclosures.")
