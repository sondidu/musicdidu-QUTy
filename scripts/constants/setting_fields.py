KEY_ANACRUSIS = 'anacrusis'
KEY_BPM = 'BPM'
KEY_SKIPBARS = 'skipbars'
KEY_TIMESIG = 'tsig'

SEP_FIELD = ','
SEP_VAL_TIMESIG = '/'
SEP_KEYVAL = '='

EXPLEN_KEYVAL = 2
EXPLEN_TIMESIG = 2

VALID_FIELDS = [
    KEY_BPM,
    KEY_TIMESIG,
    KEY_SKIPBARS
]

VALID_ANACRUSIS_VALUES = ["True", "False"]

from .notes import VALID_DURATIONS
VALID_TIMESIG_BOTTOM_VALUES = VALID_DURATIONS

BPM_MIN = 64