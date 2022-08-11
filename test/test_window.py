from unittest.mock import Mock
from ftwm.window import Window
from xcffib.xproto import ConfigWindow


def test_set_position():
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
