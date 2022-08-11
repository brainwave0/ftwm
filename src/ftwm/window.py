from xcffib import Connection
from xcffib.xproto import ConfigWindow


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
