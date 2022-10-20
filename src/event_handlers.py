from xcffib import Connection, Event

from .placement import place
from .window import Window


def handle_map_request(connection: Connection, event: Event, windows: list[Window], screen) -> None:
    window = Window(connection, event.window)  # type: ignore[attr-defined]
    connection.core.MapWindow(event.window)  # type: ignore[attr-defined]
    geometry = connection.core.GetGeometry(window.id).reply()
    window.virtual.size = (geometry.width, geometry.height)
    place(screen, windows, window)
    windows.append(window)


def handle_screen_change_notify(event, windows, screen):
    screen.width = event.width
    screen.height = event.height
    tmp_windows = []
    for window in windows:
        place(screen, tmp_windows, window)
        tmp_windows.append(window)
