
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

    def __init__(self, msg, line_no, column_no, line_content):
        self.msg = msg
        self.line_no = line_no
        self.column_no = column_no
        self.line_content = line_content

        super().__init__()

    def __str__(self):
        first_line = f"{self.line_content} at line {self.line_no}\n"
        pointer = ' ' * self.column_no + '^' + ' ' + self.msg
        return f"{self.msg} at line {self.line_no}."

class ElementError(Exception):
    """Error regarding element notation."""

    def __init__(self, element, msg=None):
        self.element = element
        self.msg = msg

        super().__init__()

    def __str__(self):
        constructed_msg = f'Invalid element "{self.element}"'
        if self.msg is not None:
            constructed_msg += ' ' + self.msg
        return constructed_msg + '.'

class FieldError(Exception):
    """Error regarding fields."""

    def __init__(self, field, msg=None):
        self.field = field
        self.msg = msg

        super().__init__()

    def __str__(self):
        constructed_msg = f'Invalid field "{self.field}"'
        if self.msg is not None:
            constructed_msg += ' ' + self.msg
        return constructed_msg + '.'

class BeatError(Exception):
    """Error regarding beat count."""

    def __init__(self, expected_beats=None, actual_beats=None, msg=None):
        self.expected_beats = expected_beats
        self.actual_beats = actual_beats
        self.msg = msg

        super().__init__()

    def __str__(self):
        if self.expected_beats is not None and self.actual_beats is not None:
            return f"Expected {self.expected_beats} beats (in 32nds) but got {self.actual_beats} instead."
        return self.msg