import math
from .screen import Screen
from .window import Window
from .rectangle import Rectangle
from copy import copy
from test.visualize_layout import visualize
from functools import reduce


def place(screen: Screen, windows: list[Window], window: Window) -> None:
    if not windows:
        window.virtual.center = screen.center
        screen.grid.set_range(window.virtual.as_list(), window)
    else:
        used_area = reduce(lambda a, b: a + b, map(lambda x: x.virtual, windows))
        top = used_area.top - window.virtual.height
        right = used_area.right + window.virtual.width
        bottom = used_area.bottom + window.virtual.height
        left = used_area.left - window.virtual.width
        # visualize([("cell",reduce(lambda a,b:a+b,(cell for cell,_ in screen.grid)).as_list()),("screen",screen.as_list())])
        screen.grid.expand(top, right, bottom, left)
        # if window.id == 6:
        #     visualize([("cell",reduce(lambda a,b:a+b,(cell for cell,_ in screen.grid)).as_list()),("screen",screen.as_list())])
        best_spot = None
        best_score = None
        for cell, value in screen.grid:
            if value is not None:
                continue
            for gravity in ['center', 'top_center', 'top_right', 'right_center', 'bottom_right', 'bottom_center', 'bottom_left', 'left_center', 'top_left']:
                spot = copy(window.virtual)
                gravity_point = getattr(cell, gravity)
                setattr(spot, gravity, gravity_point)
                if any(spot.overlaps(window_.virtual) for window_ in windows):
                    continue
                new_score = score(spot, screen)
                if best_spot is None or new_score > best_score:
                    best_spot = spot
                    best_score = new_score
        window.virtual.position = tuple(map(int, best_spot.position))
    screen.grid.set_range(window.virtual.as_list(), window)


def distance(point_a, point_b) -> float:
    dx = point_b[0] - point_a[0]
    dy = point_b[1] - point_a[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def score(spot, screen):
    visible = copy(spot)  # visible portion from the center of the screen
    visible.top = max(screen.top, visible.top)
    visible.left = max(screen.left, visible.left)
    visible.width = min(screen.right, visible.right) - visible.left
    visible.height = min(screen.bottom, visible.bottom) - visible.top
    area = visible.width * visible.height
    nearest_point = getattr(spot, get_gravity(screen, spot))
    return 1 / (distance(nearest_point, screen.center) + 1)


def get_gravity(screen, spot):
    gravities = ['top_center', 'top_right', 'right_center', 'bottom_right', 'bottom_center', 'bottom_left',
                 'left_center', 'top_left']
    return min(gravities, key=lambda g: distance(getattr(spot, g), screen.center))
