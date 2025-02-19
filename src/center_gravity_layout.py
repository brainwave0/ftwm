from copy import copy

from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle
from .screen import Screen
from .window import Window
from .state import State
from .layout import Layout
from .state import State


class CenterGravityLayout(Layout):
    def __init__(self, state: State):
        self._state = state

    def place(self, window: Window) -> None:
        """
        Places the window on the virtual desktop as close to the center as possible without overlapping other windows.
        """
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
        self._state.screen.grid.set_range(window.virtual, window)

    def _get_score(self, spot: Rectangle) -> float:
        horizontal_score = abs(
            spot.center[0] - self._state.screen.geometry.center[0]
        ) / (self._state.screen.geometry.width / 2)
        vertical_score = abs(spot.center[1] - self._state.screen.geometry.center[1]) / (
            self._state.screen.geometry.height / 2
        )
        return 1 / (horizontal_score + vertical_score + 1)
