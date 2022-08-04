from operator import add
from typing import TypeVar, Iterable
from xcffib import Connection
from xcffib.xproto import ConfigWindow
T = TypeVar('T')


class Window:
    def __init__(self, connection: Connection, id: int, virtual_position: tuple[int, int] = (0, 0)):
        self.virtual_position = virtual_position
        self._position = (0, 0)
        self.connection = connection
        self.id = id

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, other: tuple[int, int]) -> None:
        self.connection.core.ConfigureWindow(
            self.id, ConfigWindow.X | ConfigWindow.Y, list(other))
        self._position = other


def pan(windows: Iterable[Window], delta: tuple[int, int], scale: float = 1) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in windows:
        window.position = (
            int(window.virtual_position[0] + delta[0] * scale), int(window.virtual_position[1] + delta[1] * scale))
