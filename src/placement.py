import math
from copy import copy
from functools import reduce

from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle
from .screen import Screen
from .window import Window


def place(screen: Screen, windows: list[Window], window: Window) -> None:
    """
    Places the window on the virtual desktop as close to the center as possible without overlapping other windows.
    """
    assert window not in windows
    if not windows:
        # the first window goes in the center
        window.virtual.center = screen.geometry.center
        screen.grid.set_range(window.virtual, window)
    else:
        used_area = reduce(lambda a, b: a + b, map(lambda x: x.virtual, windows))

        top = used_area.top - window.virtual.height
        right = used_area.right + window.virtual.width
        bottom = used_area.bottom + window.virtual.height
        left = used_area.left - window.virtual.width
        screen.grid.expand(top, right, bottom, left)

        best_spot = None
        best_score = None
        for cell, value in screen.grid:
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
                new_score = score(spot, screen)
                if best_spot is None or new_score > best_score:
                    # update the best spot and its score
                    best_spot = spot
                    best_score = new_score

        assert best_spot is not None
        window.virtual.position = tuple(map(int, best_spot.position))

    screen.grid.set_range(window.virtual, window)


def distance(point_a: tuple[float, float], point_b: tuple[float, float]) -> float:
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return math.sqrt(dx**2 + dy**2)


def score(spot: Rectangle, screen: Screen) -> float:
    nearest_point = getattr(spot, get_gravity(screen, spot))
    return 1 / (distance(nearest_point, screen.geometry.center) + 1)


def get_gravity(screen: Screen, spot: Rectangle) -> str:
    gravities = [
        "top_center",
        "top_right",
        "right_center",
        "bottom_right",
        "bottom_center",
        "bottom_left",
        "left_center",
        "top_left",
    ]
    return min(
        gravities, key=lambda g: distance(getattr(spot, g), screen.geometry.center)
    )


def arrange(screen: Screen, windows: list[Window]) -> None:
    screen.grid = DynamicGrid()
    tmp_windows: list[Window] = []
    for window in sorted(windows, key=lambda x: x.virtual.area(), reverse=True):
        place(screen, tmp_windows, window)
        tmp_windows.append(window)
