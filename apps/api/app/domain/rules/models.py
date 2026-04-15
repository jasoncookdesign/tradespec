from enum import Enum


class EvaluationStatus(str, Enum):
    """Shared evaluation outcome vocabulary for setup-level rule checks."""

    VALID = "VALID"
    WAIT = "WAIT"
    INVALID = "INVALID"
