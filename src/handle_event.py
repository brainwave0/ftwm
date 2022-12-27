import xcffib
from xcffib import Connection
from xcffib.randr import ScreenChangeNotifyEvent
from xcffib.xproto import MapRequestEvent, DestroyNotifyEvent, ButtonPressEvent, WindowError, DrawableError

from . import hooks
from .placement import place, arrange
from .screen import Screen
from .window import Window


def map_request(connection: Connection, event: MapRequestEvent, windows: list[Window], screen: Screen) -> None:
    assert not connection.invalid()
    window = Window(connection, event.window)
    geometry = connection.core.GetGeometry(window.id).reply()
    window.virtual.size = (geometry.width, geometry.height)
    place(screen, windows, window)
    windows.append(window)
    connection.core.MapWindow(event.window)
    hooks.map_request.fire(connection, event.window)


def screen_change_notify(event: ScreenChangeNotifyEvent, windows: list[Window], screen: Screen) -> None:
    screen.geometry.width = event.width
    screen.geometry.height = event.height
    arrange(screen, windows)


def destroy_notify(event: DestroyNotifyEvent, windows: list[Window]) -> None:
    try:
        window = next(i for i in windows if i.id == event.window)
        windows.remove(window)
    except StopIteration:
        pass


def button_press(connection: Connection, event: ButtonPressEvent, windows: list[Window]) -> None:
    if any(event.event == window.id for window in windows):
        hooks.window_clicked.fire(connection, event.event, windows)
    hooks.button_pressed.fire(connection)


def handle_event(connection: Connection, windows: list[Window], screen: Screen) -> None:
    try:
        event = connection.poll_for_event()
        if event is not None:
            if isinstance(event, MapRequestEvent):
                map_request(connection, event, windows, screen)
            elif isinstance(event, ScreenChangeNotifyEvent):
                screen_change_notify(event, windows, screen)
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
        print(f"Code: {e.code}")
        print(f"Major opcode: {e.major_opcode}")
        print(f"Minor opcode: {e.minor_opcode}")
        raise e
