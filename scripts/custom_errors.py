
class InvalidSheet(Exception):
    """When a sheet is invalid."""

    def __init__(self, errors_count, regarding):
        self.errors_count = errors_count
        self.regarding = regarding
        super().__init__()

    def __str__(self):
        return f"There are {self.errors_count} errors regarding {self.regarding}."

class BlockEnclosureError(Exception):
    """Error regarding block notation."""

    def __init__(self, msg, line_no, column_no):
        self.msg = msg
        self.line_no = line_no
        self.column_no = column_no

        super().__init__()

    def __str__(self):
        return f"\t{self.msg} at line {self.line_no} column {self.column_no}."

class ElementError(Exception):
    """Error regarding element notation."""

    def __init__(self, element):
        self.element = element

        super().__init__()

    def __str__(self):
        return f'Invalid element "{self.element}"'

class BeatError(Exception):
    """Error regarding beat count."""

    def __init__(self, bar, line_no, column_no, block_no, tsig_top, tsig_bottom, actual_beats):
        self.bar = bar
        self.line_no = line_no
        self.column_no = column_no
        self.block_no = block_no

        duration_to_32nd = {
            1 : 32,
            2 : 16,
            4 : 8,
            8 : 4,
            16 : 2,
            32 : 1
        }

        self.expected_beats_32nd = tsig_top * duration_to_32nd[tsig_bottom]
        self.actual_beats = actual_beats

        super().__init__()

    def __str__(self):
        return f"Expected {self.expected_beats_32nd} beats (in 32nds) but got {self.actual_beats} instead, at line {self.line_no} column {self.column_no} block {self.block_no}."