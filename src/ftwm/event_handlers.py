from xcffib import Connection, Event
from .window import Window


def handle_map_request(connection: Connection, event: Event, windows: list[Window]) -> None:
    window = Window(connection, event.window)  # type: ignore[attr-defined]
    windows.append(window)
    connection.core.MapWindow(event.window)  # type: ignore[attr-defined]
