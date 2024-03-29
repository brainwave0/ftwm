from dbus_next import DBusError  # type: ignore[import]
from dbus_next.aio import MessageBus  # type: ignore[import]
from dbus_next.service import ServiceInterface, method  # type: ignore[import]

from src.increment import increment
from src.placement import arrange_windows
from src.screen import Screen
from src.window import Window, get_active_window
from .state import State

no_window_error = DBusError(
    "com.github.brainwave0.ftwm.error.NoWindow", "There is no active window."
)


class Interface(ServiceInterface):  # type: ignore[misc]
    def __init__(self, state: State) -> None:
        super().__init__("com.github.brainwave0.ftwm.interface")
        self.state = state

    @method()
    async def Arrange(self):  # type: ignore[no-untyped-def]
        arrange_windows(self.state)

    @method()  # type: ignore[misc]
    async def Increment(self, dimension: "s", direction: "n"):  # type: ignore[no-untyped-def, name-defined]
        window = get_active_window(self.state)
        if dimension not in ["width", "height"]:
            raise DBusError(
                "com.github.brainwave0.ftwm.error.InvalidInput",
                f'Dimension must be "width" or "height", but "{dimension}" was provided.',
            )
        elif direction not in [-1, 1]:
            raise no_window_error
        elif window is None:
            raise no_window_error
        else:
            current_value = getattr(window, dimension)
            new_value = increment((window.id, dimension), current_value, direction)
            setattr(window, dimension, new_value)

    @method()
    async def Kill(self):  # type: ignore[no-untyped-def]
        window = get_active_window(self.state)
        if window is None:
            raise no_window_error
        else:
            window.kill()


async def setup(state: State) -> None:
    bus = await MessageBus().connect()
    interface = Interface(state)
    bus.export("/com/github/brainwave0/ftwm/interface", interface)
    await bus.request_name("com.github.brainwave0.ftwm")
