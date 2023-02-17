import xcffib  # type: ignore[import]
from xcffib import Connection
from xcffib.xproto import (  # type: ignore[import]
    MapRequestEvent,
    DestroyNotifyEvent,
    ButtonPressEvent,
    WindowError,
    DrawableError,
)

from .placement import place
from .screen import Screen
from .window import Window
from .click_to_focus import register_for_button_press_events, allow_events, focus_window


def map_request(
    connection: Connection,
    event: MapRequestEvent,
    windows: list[Window],
    screen: Screen,
) -> None:
    assert not connection.invalid()
    window = Window(connection, event.window)
    geometry = connection.core.GetGeometry(window.id).reply()
    window.virtual.size = (geometry.width, geometry.height)
    place(screen, windows, window)
    windows.append(window)
    connection.core.MapWindow(event.window)
    register_for_button_press_events(connection, event.window)


def destroy_notify(event: DestroyNotifyEvent, windows: list[Window]) -> None:
    try:
        window = next(i for i in windows if i.id == event.window)
        windows.remove(window)
    except StopIteration:
        pass


def button_press(
    connection: Connection, event: ButtonPressEvent, windows: list[Window]
) -> None:
    if any(event.event == window.id for window in windows):
        focus_window(connection, event.event, windows)
    allow_events(connection)


def handle_event(connection: Connection, windows: list[Window], screen: Screen) -> None:
    try:
        event = connection.poll_for_event()
        if event is not None:
            if isinstance(event, MapRequestEvent):
                map_request(connection, event, windows, screen)
            elif isinstance(event, DestroyNotifyEvent):
                destroy_notify(event, windows)
            elif isinstance(event, ButtonPressEvent):
                button_press(connection, event, windows)
            else:
                pass
    except WindowError:
        pass
    except DrawableError:
        pass
    except xcffib.Error as e:
        raise e
