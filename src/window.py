from xcffib import Connection
from xcffib.xproto import ConfigWindow
from .rectangle import Rectangle


class Window:
    def __init__(self, connection: Connection, id: int, virtual_position: tuple[int, int]=(0, 0), size=None):
        self._position = (0, 0)
        self.connection = connection
        self.id = id
        self.virtual = Rectangle()
        self.virtual.position = virtual_position
        if size:
            self.virtual.size = size

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, other: tuple[int, int]) -> None:
        self.connection.core.ConfigureWindow(
            self.id, ConfigWindow.X | ConfigWindow.Y, list(other))
        self._position = other
