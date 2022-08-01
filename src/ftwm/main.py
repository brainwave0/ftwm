from operator import add
from typing import TypeVar, Iterable
T = TypeVar('T')


class Window:
    def __init__(self, virtual_position: tuple[int, int] = (0, 0)):
        self.virtual_position = virtual_position
        self.position = (0, 0)


def pan(windows: Iterable[Window], delta: tuple[int, int], scale: float = 1) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in windows:
        window.position = (
            int(window.virtual_position[0] + delta[0] * scale), int(window.virtual_position[1] + delta[1] * scale))
