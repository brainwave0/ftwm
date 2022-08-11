from unittest.mock import Mock
from ftwm.event_handlers import handle_map_request
from ftwm.window import Window


def test_handle_map_request():
    connection = Mock()
    event = Mock()
    event.window = 0
    windows = []
    handle_map_request(connection, event, windows)
    assert len(windows) == 1
    assert type(windows[0]) is Window
    assert windows[0].id == event.window
    connection.core.MapWindow.assert_called_once_with(event.window)
