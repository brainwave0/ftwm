from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .state import State
from .rectangle import Rectangle
from wlroots.wlr_types.xdg_shell import XdgSurface
from wlroots.wlr_types import SceneNode  # type: ignore[attr-defined]


class Window:
    def __init__(
        self,
        state: State,
        xdg_surface: XdgSurface,
        scene_node: SceneNode,
        virtual_position: tuple[int, int] = (0, 0),
        size: tuple[int, int] = (0, 0),
    ) -> None:
        assert size[0] >= 0 and size[1] >= 0
        self._position = (0, 0)
        self._state = state
        self.virtual = Rectangle()
        self.virtual.position = virtual_position
        self.virtual.size = size
        self.active = False
        self._xdg_surface = xdg_surface
        self._scene_node = scene_node
        self.id = state.new_id()

    @property
    def position(self) -> tuple[int, int]:
        return self._position

    @position.setter
    def position(self, other: tuple[int, int]) -> None:
        if self._position != other:
            self._scene_node.set_position(*other)
            self._position = other

    @property
    def width(self) -> float:
        return self.virtual.width

    @width.setter
    def width(self, other: int) -> None:
        self.virtual.width = other
        self._xdg_surface.set_size(max(1, other), int(self.virtual.height))

    @property
    def height(self) -> float:
        return self.virtual.height

    @height.setter
    def height(self, other: int) -> None:
        self.virtual.height = other
        self._xdg_surface.set_size(int(self.virtual.width), max(1, other))

    def kill(self) -> None:
        self._xdg_surface.send_close()
        self._state.windows.remove(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Window):
            return NotImplemented
        return self.id == other.id
