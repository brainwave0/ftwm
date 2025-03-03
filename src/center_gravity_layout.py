from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .state import State
from copy import copy

from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle
from .screen import Screen
from .window import Window
from .layout import Layout


class CenterGravityLayout(Layout):
    def __init__(self, state: State):
        self._state = state

    def arrange(self) -> None:
        self._state.screen.grid = DynamicGrid()
        for window in sorted(
            self._state.windows, key=lambda window: window.virtual.area(), reverse=True
        ):
            self.place(window)

    def place(self, window: Window) -> None:
        """
        Places the window on the virtual desktop as close to the center as possible without overlapping other windows.
        """
        all_window_rect = sum((w.virtual for w in self._state.windows), Rectangle())
        all_window_rect.width += window.width * 2
        all_window_rect.height += window.height * 2
        all_window_rect.center = self._state.screen.geometry.center
        self._state.screen.grid.make_area(all_window_rect)
        best_spot = None
        best_score = None
        for cell, contents in self._state.screen.grid:
            if contents is None:
                # try each gravity and see how well the window fits when anchored there
                for gravity in [
                    "center",
                    "top_center",
                    "top_right",
                    "right_center",
                    "bottom_right",
                    "bottom_center",
                    "bottom_left",
                    "left_center",
                    "top_left",
                ]:
                    spot = copy(
                        window.virtual
                    )  # make copy of the window rectangle for testing purposes

                    # anchor it in the cell
                    gravity_point = getattr(cell, gravity)
                    setattr(spot, gravity, gravity_point)

                    if self._state.screen.grid.empty(spot):
                        new_score = self._get_score(spot)
                        if best_spot is None or new_score > best_score:
                            # update the best spot and its score
                            best_spot = spot
                            best_score = new_score
        assert best_spot is not None
        window.virtual.position = best_spot.position
        self._state.screen.grid.set_area(window.virtual, window)

    def _get_score(self, spot: Rectangle) -> float:
        horizontal_score = abs(
            spot.center[0] - self._state.screen.geometry.center[0]
        ) / (self._state.screen.geometry.width / 2)
        vertical_score = abs(spot.center[1] - self._state.screen.geometry.center[1]) / (
            self._state.screen.geometry.height / 2
        )
        return 1 / (horizontal_score + vertical_score + 1)
