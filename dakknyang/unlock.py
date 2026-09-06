from dataclasses import dataclass


@dataclass(slots=True)
class UnlockState:
    """UI-independent state machine for the two-step unlock gesture."""

    required_presses: int = 5
    character_armed: bool = False
    press_count: int = 0

    def __post_init__(self) -> None:
        if self.required_presses < 1:
            raise ValueError("required_presses must be at least 1")

    @property
    def remaining(self) -> int:
        return max(0, self.required_presses - self.press_count)

    @property
    def is_unlocked(self) -> bool:
        return self.character_armed and self.remaining == 0

    def arm(self) -> None:
        self.character_armed = True
        self.press_count = 0

    def register_space(self) -> bool:
        if not self.character_armed or self.is_unlocked:
            return False
        self.press_count += 1
        return self.is_unlocked

