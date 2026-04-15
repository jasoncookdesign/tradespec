from dataclasses import dataclass


@dataclass(slots=True)
class ExpectedBehaviorEnvelope:
    """Represents the normal price behavior range after a trade is opened."""

    thesis_holds: bool
    note: str


class ActiveTradeStabilizerService:
    def evaluate_behavior(self) -> ExpectedBehaviorEnvelope:
        return ExpectedBehaviorEnvelope(
            thesis_holds=True,
            note="Active-trade stabilizer logic will be implemented in a later step.",
        )
