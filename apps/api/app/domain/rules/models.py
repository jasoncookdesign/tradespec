from enum import Enum


class EvaluationStatus(str, Enum):
    """Shared evaluation outcome vocabulary for setup-level rule checks."""

    # TODO: This status set is currently shared by ticker evaluation and trade
    # validation. Split it later if those semantics begin to diverge.
    VALID = "VALID"
    WAIT = "WAIT"
    INVALID = "INVALID"
