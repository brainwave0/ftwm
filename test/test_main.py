from ftwm.main import *
from unittest.mock import Mock
from xcffib.xproto import ConfigWindow


def test_pan():
    windows = [Window(Mock(), 0, virtual_position=(0, 0))]
    pan(windows, (-1, 1), scale=2)
    assert windows[0].position == (-2, 2)

    windows = [Window(Mock(), 0, virtual_position=(1, -1))]
    pan(windows, (0, 1), scale=1)
    assert windows[0].position == (1, 0)

    windows = [Window(Mock(), 0, virtual_position=(2, -3)),
               Window(Mock(), 1, virtual_position=(2, -1))]
    pan(windows, (-2, -1), scale=2)
    assert windows[0].position == (-2, -5)
    assert windows[1].position == (-2, -3)

    windows = [Window(Mock(), 0, virtual_position=(3, -1))]
    pan(windows, (0, 0), scale=2)
    assert windows[0].position == (3, -1)


class TestWindow:
    def test_set_position(self):
        connection = Mock()
        window = Window(connection, 1)
        window.position = (-3, -2)
        connection.core.ConfigureWindow.assert_called_once_with(
            1, ConfigWindow.X | ConfigWindow.Y, [-3, -2])

        connection = Mock()
        window = Window(connection, 1)
        window.position = (1, 1)
        connection.core.ConfigureWindow.assert_called_once_with(
            1, ConfigWindow.X | ConfigWindow.Y, [1, 1])
