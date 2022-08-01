from ftwm.main import *


def test_pan():
    windows = [Window(virtual_position=(0, 0))]
    pan(windows, (-1, 1), scale=2)
    assert windows[0].position == (-2, 2)

    windows = [Window(virtual_position=(1, -1))]
    pan(windows, (0, 1), scale=1)
    assert windows[0].position == (1, 0)

    windows = [Window(virtual_position=(2, -3)),
               Window(virtual_position=(2, -1))]
    pan(windows, (-2, -1), scale=2)
    assert windows[0].position == (-2, -5)
    assert windows[1].position == (-2, -3)

    windows = [Window(virtual_position=(3, -1))]
    pan(windows, (0, 0), scale=2)
    assert windows[0].position == (3, -1)
