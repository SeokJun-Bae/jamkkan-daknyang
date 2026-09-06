import pytest

from dakknyang.unlock import UnlockState


def test_space_does_nothing_before_character_click() -> None:
    state = UnlockState(required_presses=5)
    assert state.register_space() is False
    assert state.press_count == 0


def test_unlocks_after_required_number_of_presses() -> None:
    state = UnlockState(required_presses=3)
    state.arm()

    assert state.register_space() is False
    assert state.register_space() is False
    assert state.register_space() is True
    assert state.is_unlocked is True


def test_clicking_character_again_restarts_count() -> None:
    state = UnlockState(required_presses=3)
    state.arm()
    state.register_space()
    state.arm()
    assert state.remaining == 3


def test_invalid_required_count_is_rejected() -> None:
    with pytest.raises(ValueError, match="required_presses"):
        UnlockState(required_presses=0)
