from constants.block import *

def validate_blocks(content: str):
    bar_chars = set((BAR_OPEN, BAR_CLOSE))
    setting_chars = set((SETTING_OPEN, SETTING_CLOSE))
    block_chars = bar_chars | setting_chars
    errors_count = 0

    for line_no, line in enumerate(content.splitlines(), start=1):
        bar_opened_idx = None
        setting_opened_idx = None
        nonblock_char_startidx = None

        for column_no, char in enumerate(line):
            # Skip non-block chars
            if not char in block_chars:

                # Mark non-block char if no block has been opened, ignore if whitespace
                if nonblock_char_startidx == \
                    bar_opened_idx == \
                    setting_opened_idx == None \
                    and not char.isspace():
                    nonblock_char_startidx = column_no

                continue

            if nonblock_char_startidx != None:
                print(f"Non-block string '{content[nonblock_char_startidx:column_no]}' at line {line_no} column {nonblock_char_startidx} but no block '{BAR_OPEN}' or '{SETTING_OPEN} was opened.")
                errors_count += 1
                nonblock_char_startidx = None

            if bar_opened_idx == None and setting_opened_idx == None:
                if char == BAR_OPEN:
                    bar_opened_idx = column_no
                if char == BAR_CLOSE:
                    print(f"Bar was closed '{BAR_CLOSE}' but was never opened at line {line_no} column {column_no}.")
                    errors_count += 1

                if char == SETTING_OPEN:
                    setting_opened_idx = column_no
                if char == SETTING_CLOSE:
                    print(f"Setting block was closed '{SETTING_CLOSE}' but never opened at line {line_no} column {column_no}.")
                    errors_count += 1

            elif bar_opened_idx != None:
                unallowed_chars = block_chars - {BAR_CLOSE}
                if char in unallowed_chars:
                    print(f"Bar '{BAR_OPEN}' is still opened at line {line_no} column {bar_opened_idx} but '{char}' was found at line {line_no} column {column_no}.")
                    errors_count += 1
                else:
                    current_bar = content[bar_opened_idx:column_no + 1]
                    content_within = current_bar[1:-1].strip()
                    if content_within == '':
                        print(f"Empty bar '{current_bar}' at line at line {line_no} column {bar_opened_idx}.")
                        errors_count += 1
                    bar_opened_idx = None # Bar closed

            elif setting_opened_idx != None:
                unallowed_chars = block_chars - {SETTING_CLOSE}
                if char in unallowed_chars:
                    print(f"Setting block '{SETTING_OPEN}' is still opened at line {line_no} column {setting_opened_idx} but '{char}' was found at line {line_no} column {column_no}.")
                    errors_count += 1
                else:
                    current_setting_block = content[setting_opened_idx:column_no + 1]
                    content_within = current_setting_block[1:-1].strip()
                    if content_within == '':
                        print(f"Empty setting block '{current_setting_block}'at line {line_no} column {setting_opened_idx}.")
                        errors_count += 1
                    setting_opened_idx = None # Setting closed

        if bar_opened_idx != None:
            print(f"Bar was opened '{BAR_OPEN}' at line {line_no} column {bar_opened_idx} but never closed '{BAR_CLOSE}'.")
            errors_count += 1
        if setting_opened_idx != None:
            print(f"Setting block was opened '{SETTING_OPEN}' at line {line_no} column {setting_opened_idx} but never closed '{SETTING_CLOSE}'.")
            errors_count += 1

        if nonblock_char_startidx != None:
            print(f"Non-block string '{content[nonblock_char_startidx:]}' at line {line_no} column {nonblock_char_startidx} but no block '{BAR_OPEN}' or '{SETTING_OPEN} was opened.")
            errors_count += 1


    if errors_count == 0:
        print('No errors found.')
    return errors_count
