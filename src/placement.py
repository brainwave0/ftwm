from copy import copy
from functools import reduce

from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle
from .screen import Screen
from .window import Window
from .state import State


def place(state: State, windows: list[Window], window: Window) -> None:
    """
    Places the window on the virtual desktop as close to the center as possible without overlapping other windows.
    """
    assert window not in windows
    if not windows:
        # the first window goes in the center
        window.virtual.center = state.screen.geometry.center
        state.screen.grid.set_range(window.virtual, window)
    else:
        used_area = reduce(lambda a, b: a + b, map(lambda x: x.virtual, windows))

        top = used_area.top - window.virtual.height
        right = used_area.right + window.virtual.width
        bottom = used_area.bottom + window.virtual.height
        left = used_area.left - window.virtual.width
        state.screen.grid.expand(top, right, bottom, left)

        best_spot = None
        best_score = None
        for cell, value in state.screen.grid:
            if value is not None:
                # cell is not empty, so skip it
                continue

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

                # anchor it to the cell
                gravity_point = getattr(cell, gravity)
                setattr(spot, gravity, gravity_point)

                if any(spot.overlaps(window_.virtual) for window_ in windows):
                    # it would overlap at least one existing window, so skip
                    continue
                new_score = get_score(state, spot)
                if best_spot is None or new_score > best_score:
                    # update the best spot and its score
                    best_spot = spot
                    best_score = new_score

        assert best_spot is not None
        window.virtual.position = best_spot.position

    state.screen.grid.set_range(window.virtual, window)


def get_score(state: State, spot: Rectangle) -> float:
    horizontal_score = abs(spot.center[0] - state.screen.geometry.center[0]) / (
        state.screen.geometry.width / 2
    )
    vertical_score = abs(spot.center[1] - state.screen.geometry.center[1]) / (
        state.screen.geometry.height / 2
    )
    return 1 / (horizontal_score + vertical_score + 1)


def arrange_windows(state: State) -> None:
    state.screen.grid = DynamicGrid()
    tmp_windows: list[Window] = []
    for window in sorted(state.windows, key=lambda x: x.virtual.area(), reverse=True):
        place(state, tmp_windows, window)
        tmp_windows.append(window)
