import asyncio
from os import environ

import cv2  # type: ignore[import]
from xcffib import connect, Connection  # type: ignore[import]

from .event import handle_event
from .face_tracking import get_face_delta, get_face_detections
from .jitter_filter import JitterFilter
from .moving_average_filter import MovingAverageFilter
from .misc import (
    register_wm,
    pan,
    get_settings,
    get_and_set_up_camera,
    pan_windows_with_face,
)
from .screen import Screen
from .window import Window
from threading import Thread
import time
import src.dbus as dbus
from xdg import xdg_config_home  # type: ignore[import]
from mediapipe.python.solutions.face_detection import FaceDetection  # type: ignore[import]
from .state import State


def handle_events(state: State) -> None:
    while True:
        handle_event(state)
        time.sleep(1 / state.settings.getfloat("DEFAULT", "event_handling_rate"))


async def main() -> None:
    settings = get_settings()
    connection = connect(environ["DISPLAY"])
    register_wm(connection)
    windows: list[Window] = []
    root = connection.get_setup().roots[0]
    screen = Screen(root.width_in_pixels, root.height_in_pixels)
    state = State(settings, connection, windows, screen)
    await dbus.setup(state)
    Thread(
        target=handle_events,
        args=(state,),
        daemon=True,
    ).start()
    await pan_windows_with_face(state)


asyncio.run(main())
