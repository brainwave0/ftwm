import asyncio


from .event_handlers import register_events
from .panning import pan_windows_with_face
from .util import get_settings
from .screen import Screen
from .window import Window
import src.dbus as dbus
from .state import State
from pywayland.server import Display  # type: ignore[attr-defined]


from wlroots.wlr_types import (  # type: ignore[attr-defined]
    Seat,
    OutputLayout,
    XdgShell,
    Cursor,
    Scene,
    DataDeviceManager,
    XCursorManager,
)
from wlroots.helper import build_compositor
from wlroots.util.log import log_init
from pywayland import lib
import os


async def dispatch_events(state: State) -> None:
    loop = state.display.get_event_loop()
    while True:
        loop.dispatch(0)
        state.display.flush_clients()
        await asyncio.sleep(1 / state.settings.getfloat("DEFAULT", "frame_rate"))


async def main():
    # initialization
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
            state = State(
                settings,
                windows,
                Screen(0, 0),
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
            register_events(state)

            # running
            with backend:  # start the backend
                async with asyncio.TaskGroup() as group:
                    for function in (pan_windows_with_face, dbus.setup, dispatch_events):
                        tasks[function.__name__] = group.create_task(function(state))

asyncio.run(main())
