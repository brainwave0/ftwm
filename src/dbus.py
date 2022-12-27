from dbus_next import DBusError
from dbus_next.aio import MessageBus
from dbus_next.service import ServiceInterface, method

from src import hooks
from src.increment import increment
from src.placement import arrange
from src.screen import Screen
from src.window import Window, active_window


class Interface(ServiceInterface):
    def __init__(self, screen: Screen, windows: list[Window]) -> None:
        super().__init__('com.github.brainwave0.ftwm.interface')
        self.screen = screen
        self.windows = windows

    @method()
    async def Arrange(self):
        arrange(self.screen, self.windows)

    @method()
    async def Increment(self, dimension: 's', direction: 'n'):
        if dimension not in ["width", "height"]:
            raise DBusError('com.github.brainwave0.ftwm.error.InvalidInput',
                            f'Dimension must be "width" or "height", but "{dimension}" was provided.')
        elif direction not in [-1, 1]:
            raise DBusError('com.github.brainwave0.ftwm.error.InvalidInput',
                            f'Dimension must be "-1" or "1", but "{direction}" was provided.')
        else:
            window = active_window(self.windows)
            current_value = getattr(window, dimension)
            new_value = increment((window.id, dimension), current_value, direction)
            setattr(window, dimension, new_value)


async def setup(screen: Screen, windows: list[Window]) -> None:
    bus = await MessageBus().connect()
    interface = Interface(screen, windows)
    bus.export('/com/github/brainwave0/ftwm/interface', interface)
    await bus.request_name('com.github.brainwave0.ftwm')


def register() -> None:
    hooks.main_initializing.register(setup)
