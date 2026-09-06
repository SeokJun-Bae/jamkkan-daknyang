import pytest

from dakknyang.config import AppConfig


def test_default_config_is_safe() -> None:
    config = AppConfig()
    assert config.unlock_press_count == 5
    assert config.auto_unlock_seconds == 60


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        ({"unlock_press_count": 0}, "unlock_press_count"),
        ({"auto_unlock_seconds": 9}, "auto_unlock_seconds"),
    ],
)
def test_invalid_config_is_rejected(kwargs: dict, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        AppConfig(**kwargs)
