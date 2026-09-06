from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AppConfig:
    """Runtime options kept in one place for later settings-screen support."""

    unlock_press_count: int = 5
    auto_unlock_seconds: int = 60

    def __post_init__(self) -> None:
        if self.unlock_press_count < 1:
            raise ValueError("unlock_press_count must be at least 1")
        if self.auto_unlock_seconds < 10:
            raise ValueError("auto_unlock_seconds must be at least 10")

