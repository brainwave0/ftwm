from xcffib import Connection
from xcffib.xproto import ConfigWindow

from .rectangle import Rectangle


class Window:
    def __init__(self, connection: Connection, id: int, virtual_position: tuple[int, int] = (0, 0),
                 size=(0, 0)) -> None:
        assert not connection.invalid()
        assert size[0] >= 0 and size[1] >= 0
        self._position = (0, 0)
        self.connection = connection
        self.id = id
        self.virtual = Rectangle()
        self.virtual.position = virtual_position
        if size:
            self.virtual.size = size
        self.active = False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, other: tuple[int, int]) -> None:
        if self._position != other:
            self.connection.core.ConfigureWindow(
                self.id, ConfigWindow.X | ConfigWindow.Y, list(other))
            self._position = other

    @property
    def width(self):
        return self.virtual.width

    @width.setter
    def width(self, other):
        self.virtual.width = other
        self.connection.core.ConfigureWindow(self.id, ConfigWindow.Width, [max(1, int(other))])

    @property
    def height(self):
        return self.virtual.height

    @height.setter
    def height(self, other):
        self.virtual.height = other
        self.connection.core.ConfigureWindow(self.id, ConfigWindow.Height, [max(1, int(other))])


def active_window(windows: list[Window]) -> Window:
    return next((window for window in windows if window.active), None)
