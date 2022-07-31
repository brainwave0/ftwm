from ftwm.main import *


def test_pan_windows():
    windows = [Window(position=(0, 0))]
    pan(windows, (-1, 1), scale=2)
    assert windows[0].position == (0, 0)
