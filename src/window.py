from xcffib import Connection  # type: ignore[import]
from xcffib.xproto import ConfigWindow  # type: ignore[import]

from .rectangle import Rectangle
from typing import Optional
from .state import State


class Window:
    def __init__(
        self,
        state: State,
        id: int,
        virtual_position: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (0, 0),
    ) -> None:
        assert not state.connection.invalid()
        assert size[0] >= 0 and size[1] >= 0
        self._position = (0, 0)
        self.state = state
        self.id = id
        self.virtual = Rectangle()
        self.virtual.position = virtual_position
        self.virtual.size = size
        self.active = False

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, other: tuple[int, int]) -> None:
        if self._position != other:
            self.state.connection.core.ConfigureWindow(
                self.id, ConfigWindow.X | ConfigWindow.Y, list(other)
            )
            self._position = other

    @property
    def width(self) -> float:
        return self.virtual.width

    @width.setter
    def width(self, other: int) -> None:
        self.virtual.width = other
        self.state.connection.core.ConfigureWindow(
            self.id, ConfigWindow.Width, [max(1, int(other))]
        )

    @property
    def height(self) -> float:
        return self.virtual.height

    @height.setter
    def height(self, other: int) -> None:
        self.virtual.height = other
        self.state.connection.core.ConfigureWindow(
            self.id, ConfigWindow.Height, [max(1, int(other))]
        )

    def kill(self) -> None:
        self.state.connection.core.KillClient(self.id)


def get_active_window(state: State) -> Optional[Window]:
    return next((window for window in state.windows if window.active), None)
