from __future__ import annotations
from typing import TYPE_CHECKING, Optional
if TYPE_CHECKING:
    from .state import State
from abc import ABC, abstractmethod
from .window import Window
from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle


class Layout(ABC):
    def __init__(self, state: State) -> None:
        self._state = state

    @abstractmethod
    def arrange(self) -> None:
        pass

    @abstractmethod
    def place(self, window: Window) -> None:
        pass

    def window_at(self, x: int, y: int) -> Optional[Window]:
        return next((i for i in self._state.windows if Rectangle(x, y, 0, 0) in i.virtual), None)
