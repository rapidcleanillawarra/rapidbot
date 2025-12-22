# Audio utilities for beep sounds
import winsound
from config import BEEP_FREQUENCIES, BEEP_DURATION


def beep(process_number: int) -> None:
    """Play a beep sound for the specified process number."""
    frequency = BEEP_FREQUENCIES.get(process_number, 1000)
    winsound.Beep(frequency, BEEP_DURATION)


def beep_custom(frequency: int, duration: int = 200) -> None:
    """Play a custom beep sound."""
    winsound.Beep(frequency, duration)


def beep_success() -> None:
    """Play a success sound (high pitch)."""
    winsound.Beep(1500, 300)


def beep_error() -> None:
    """Play an error sound (low pitch)."""
    winsound.Beep(400, 500)
