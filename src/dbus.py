from dbus_next import DBusError  # type: ignore[import]
from dbus_next.aio import MessageBus  # type: ignore[import]
from dbus_next.service import ServiceInterface, method  # type: ignore[import]

from src.increment import increment
from src.placement import arrange
from src.screen import Screen
from src.window import Window, active_window

no_window_error = DBusError(
    "com.github.brainwave0.ftwm.error.NoWindow", "There is no window."
)


class Interface(ServiceInterface):  # type: ignore[misc]
    def __init__(self, screen: Screen, windows: list[Window]) -> None:
        super().__init__("com.github.brainwave0.ftwm.interface")
        self.screen = screen
        self.windows = windows

    @method()
    async def Arrange(self):  # type: ignore[no-untyped-def]
        arrange(self.screen, self.windows)

    @method()  # type: ignore[misc]
    async def Increment(self, dimension: "s", direction: "n"):  # type: ignore[no-untyped-def, name-defined]
        window = active_window(self.windows)
        if dimension not in ["width", "height"]:
            raise DBusError(
                "com.github.brainwave0.ftwm.error.InvalidInput",
                f'Dimension must be "width" or "height", but "{dimension}" was provided.',
            )
        elif direction not in [-1, 1]:
            raise no_window_error
        elif window is None:
            raise DBusError(
                "com.github.brainwave0.ftwm.error.NoWindow",
                f"There is no active window.",
            )
        else:
            current_value = getattr(window, dimension)
            new_value = increment((window.id, dimension), current_value, direction)
            setattr(window, dimension, new_value)

    @method()
    async def Kill(self):  # type: ignore[no-untyped-def]
        window = active_window(self.windows)
        if window is None:
            raise no_window_error
        else:
            window.kill()


async def setup(screen: Screen, windows: list[Window]) -> None:
    bus = await MessageBus().connect()
    interface = Interface(screen, windows)
    bus.export("/com/github/brainwave0/ftwm/interface", interface)
    await bus.request_name("com.github.brainwave0.ftwm")
