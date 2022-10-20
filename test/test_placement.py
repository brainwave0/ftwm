from unittest.mock import Mock

from .visualize_layout import visualize
from src.placement import *
from src.rectangle import Rectangle
import math


def test_place():
    connection = Mock()
    windows = []
    screen = Screen()
    screen.size = (1920, 1080)

    id = 0
    window = Window(connection, id, size=(326, 824))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (797, 128)

    id = 1
    window = Window(connection, id, size=(852, 865))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (-55, 107)

    id = 2
    window = Window(connection, id, size=(322, 824))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (1123, 128)

    id = 3
    window = Window(connection, id, size=(529, 281))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (1445, 399)

    id = 4
    window = Window(connection, id, size=(269, 551))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (1445, -152)

    id = 5
    window = Window(connection, id, size=(670, 556))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (1445, 680)

    id = 6
    window = Window(connection, id, size=(723, 623))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (722, -516)

    id = 7
    window = Window(connection, id, size=(292, 659))
    place(screen, windows, window)
    windows.append(window)
    # assert window.virtual.position == (814, 952)
    visualize(({f"window {win.id}":win.virtual.as_list() for win in windows}|{"screen": screen.as_list()}).items())


    del windows[2]
    id = 8
    window = Window(connection, id, size=(322, 286))
    place(screen, windows, window)
    windows.append(window)
    assert window.virtual.position == (1123, 397)


def test_distance():
    assert distance((0, 0), (1, 1)) == math.sqrt(2)
    assert distance((0, 0), (-1, -1)) == math.sqrt(2)
    assert distance((0, 0), (0, 0)) == 0


def test_score():
    screen = Rectangle(0, 0, 1920, 1080)

    r1 = Rectangle(0, 0, 10, 10)
    r1.center = screen.center
    r2 = Rectangle(0, 0, 10, 10)
    r2.top_left = screen.top_left
    assert score(screen, r1) > score(screen, r2)

    r1 = Rectangle(0, 0, 10, 10)
    r1.center = screen.top_center
    r2 = Rectangle(0, 0, 10, 10)
    r2.bottom_center = screen.bottom_center
    assert score(screen, r1) < score(screen, r2)

    r1 = Rectangle(0, 0, 10, 10)
    r1.left_center = screen.left_center
    r2 = Rectangle(0, 0, 10, 10)
    r2.right_center = screen.right_center
    assert score(screen, r1) == score(screen, r2)

    r1 = Rectangle(0, 0, 10, 20)
    r1.left_center = screen.left_center
    r2 = Rectangle(0, 0, 10, 10)
    r2.right_center = screen.right_center
    assert score(screen, r1) > score(screen, r2)


def test_get_gravity():
    screen = Rectangle(0, 0, 1920, 1080)

    spot = Rectangle(0, 0, 10, 10)
    spot.top_center = screen.top_center
    assert get_gravity(screen, spot) == 'bottom_center'

    spot = Rectangle(0, 0, 10, 10)
    spot.top_right = screen.top_right
    assert get_gravity(screen, spot) == 'bottom_left'

    spot = Rectangle(0, 0, 10, 1080)
    spot.top_right = screen.top_right
    assert get_gravity(screen, spot) == 'left_center'
