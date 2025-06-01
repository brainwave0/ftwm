from dbus_next import DBusError  # type: ignore[attr-defined]
from dbus_next.aio import MessageBus  # type: ignore[attr-defined]
from dbus_next.service import ServiceInterface, method

from src.increment import increment
from .state import State

no_window_error = DBusError(  # type: ignore[no-untyped-call]
    "com.github.brainwave0.ftwm.error.NoWindow", "There is no active window."
)


class Interface(ServiceInterface):
    def __init__(self, state: State) -> None:
        super().__init__("com.github.brainwave0.ftwm.interface")
        self._state = state

    @method()
    async def Arrange(self):  # type: ignore[no-untyped-def]
        self._state.layout.arrange()

    @method()  # type: ignore[misc]
    async def Increment(self, dimension: "s", direction: "n"):  # type: ignore[no-untyped-def, name-defined]
        window = self._state.get_active_window()
        if dimension not in ["width", "height"]:
            raise DBusError(  # type: ignore[no-untyped-call]
                "com.github.brainwave0.ftwm.error.InvalidInput",
                f'Dimension must be "width" or "height", but "{dimension}" was provided.',
            )
        elif direction not in [-1, 1]:
            raise DBusError(  # type: ignore[no-untyped-call]
                "com.github.brainwave0.ftwm.error.InvalidInput",
                f'Direction must be -1 or 1, but "{direction}" was provided.',
            )
        elif window is None:
            raise no_window_error
        else:
            current_value = getattr(window, f"get_{dimension}")()
            new_value = increment((window.id, dimension), current_value, direction)
            getattr(window, f"set_{dimension}")(int(new_value))

    @method()
    async def Kill(self):  # type: ignore[no-untyped-def]
        window = self._state.get_active_window()
        if window is None:
            raise no_window_error
        else:
            window.kill()


async def setup(state: State) -> None:
    bus = await MessageBus().connect()
    interface = Interface(state)
    bus.export("/com/github/brainwave0/ftwm/interface", interface)
    await bus.request_name("com.github.brainwave0.ftwm")
