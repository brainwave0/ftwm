from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .state import State
from .rectangle import Rectangle
from wlroots.wlr_types.xdg_shell import XdgSurface
from wlroots.wlr_types import SceneNode  # type: ignore[attr-defined]


class Window(Rectangle):
    def __init__(
        self,
        state: State,
        xdg_surface: XdgSurface,
        scene_node: SceneNode,
        size: tuple[float, float] = (0, 0),
    ) -> None:
        Rectangle.__init__(self)
        assert size[0] >= 0 and size[1] >= 0
        self._state = state
        self.active = False
        self._xdg_surface = xdg_surface
        self._scene_node = scene_node
        self.size = size
        self.id = state.new_id()

    def kill(self) -> None:
        self._xdg_surface.send_close()
        self._state.windows.remove(self)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Window):
            return NotImplemented
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)

    def set_position(self, other: tuple[float, float]) -> None:
        Rectangle.set_position(self, other)
        if self.get_position() != other:
            self._scene_node.set_position(*tuple(map(int, other)))

    def set_width(self, other: float) -> None:
        Rectangle.set_width(self, other)
        self._xdg_surface.set_size(int(max(1, other)), int(self.get_height()))

    def set_height(self, other: float) -> None:
        Rectangle.set_height(self, other)
        self._xdg_surface.set_size(int(max(1, other)), int(self.get_height()))

    def set_size(self, other: tuple[float, float]) -> None:
        Rectangle.set_size(self, other)
        self._xdg_surface.set_size(int(other[0]), int(other[1]))
