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

    @abstractmethod
    def arrange(self) -> None:
        pass

    @abstractmethod
    def place(self, window: Window) -> None:
        pass
