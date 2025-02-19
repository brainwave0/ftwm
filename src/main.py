import asyncio


from .event_handlers import register_events
from .panning import pan_windows_with_face
from .util import get_settings
from .screen import Screen
from .window import Window
import src.dbus as dbus
from .state import State
from pywayland.server import Display  # type: ignore[attr-defined]

# type: ignore[attr-defined]
from wlroots.wlr_types import (
    Seat,
    OutputLayout,
    XdgShell,
    Cursor,
    Scene,
    DataDeviceManager,
    XCursorManager,
)
from wlroots.helper import build_compositor
from threading import Thread
import logging
from wlroots.util.log import log_init
from pywayland import lib


async def dispatch_events(state: State) -> None:
    loop = state.display.get_event_loop()
    while True:
        loop.dispatch(0)
        state.display.flush_clients()
        await asyncio.sleep(0)


# initialization
log_init(logging.INFO)
logging.basicConfig(level=logging.INFO)
settings = get_settings()
windows: list[Window] = []
tasks: dict[str, asyncio.Task[None]] = {}
with Display() as display:
    compositor, allocator, renderer, backend, subcompositor = build_compositor(display)
    device_manager = DataDeviceManager(display)
    xdg_shell = XdgShell(display)
    with OutputLayout() as output_layout, Cursor(
        output_layout
    ) as cursor, XCursorManager(None, 24) as xcursor_manager, Seat(
        display, "seat0"
    ) as seat:
        scene = Scene()
        scene_layout = scene.attach_output_layout(output_layout)
        dimensions = output_layout.get_box()
        screen = Screen(dimensions.width, dimensions.height)
        state = State(
            settings,
            windows,
            screen,
            tasks,
            False,
            seat,
            scene,
            cursor,
            xdg_shell,
            backend,
            scene_layout,
            allocator,
            renderer,
            output_layout,
            display,
        )
        socket = display.add_socket()
        logging.info(f"socket: {socket.decode()}")
        register_events(state)

        # running
        event_loop = asyncio.new_event_loop()
        for function in (pan_windows_with_face, dbus.setup, dispatch_events):
            tasks[function.__name__] = event_loop.create_task(function(state))
        with backend:  # start the backend
            event_loop.run_forever()
