from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .state import State
from abc import ABC, abstractmethod
from .window import Window
from .dynamic_grid import DynamicGrid


class Layout(ABC):
    def __init__(self, state: State) -> None:
        self._state = state

    def arrange(self) -> None:
        self._state.screen.grid = DynamicGrid()
        for window in sorted(
            self._state.windows, key=lambda window: window.virtual.area(), reverse=True
        ):
            self.place(window)

    @abstractmethod
    def place(self, window: Window) -> None:
        pass
