from abc import ABC, abstractmethod
from .state import State
from .window import Window
from .dynamic_grid import DynamicGrid


class Layout(ABC):
    def __init__(self, state: State) -> None:
        self._state = state
        self.arrange()

    def arrange(self) -> None:
        self._state.screen.grid = DynamicGrid()
        temp_windows = self._state.windows
        self._state.windows = []
        for window in sorted(
            temp_windows, key=lambda window: window.virtual.area(), reverse=True
        ):
            self.place(window)

    @abstractmethod
    def place(self, window: Window) -> None:
        pass
