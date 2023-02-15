import asyncio
from os import environ

import cv2
from mediapipe.python.solutions.face_detection import FaceDetection
from xcffib import connect, Connection

from .event import handle_event
from .face_tracking import face_delta, face_detections
from .jitter_filter import JitterFilter
from .moving_average_filter import MovingAverageFilter
from .misc import register_wm, pan
from .screen import Screen
from .window import Window
from threading import Thread
import logging
from glob import glob
import time
import src.dbus as dbus
from xdg import xdg_config_home
from configparser import ConfigParser
from pathlib import Path
import shutil
from os import makedirs


def handle_events(
    connection: Connection, windows: list[Window], screen: Screen, frame_rate: float
) -> None:
    while True:
        handle_event(connection, windows, screen)
        time.sleep(1 / frame_rate / 2)


def automatically_select_camera(face_detector) -> cv2.VideoCapture:
    for index in sorted(
        int(device.replace("/dev/video", "")) for device in glob("/dev/video*")
    ):
        camera = cv2.VideoCapture(index)
        _, frame = camera.read()
        if frame is not None:
            detections = face_detections(face_detector, frame)
            if detections:
                return camera
        camera.release()
    return None


async def main() -> None:
    source_directory = Path(__file__).resolve().parent
    settings_file_path = xdg_config_home() / "ftwm/settings.ini"
    if not settings_file_path.is_file():
        makedirs(settings_file_path.parent, exist_ok=True)
        shutil.copy(source_directory.parent / "settings.ini", settings_file_path)
    settings = ConfigParser()
    settings.read(settings_file_path)

    connection = connect(environ["DISPLAY"])
    register_wm(connection)
    face_detector = FaceDetection(model_selection=0, min_detection_confidence=0)
    camera = (
        cv2.VideoCapture(settings.getint("Camera", "index"))
        if "index" in settings["Camera"]
        else automatically_select_camera(face_detector)
    )
    camera.set(cv2.CAP_PROP_FPS, settings.getint("Camera", "fps"))
    if "capture_width" in settings["Camera"] and "capture_height" in settings["Camera"]:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, settings.getint("Camera", "capture_width"))
        camera.set(
            cv2.CAP_PROP_FRAME_WIDTH, settings.getint("Camera", "capture_height")
        )
    windows: list[Window] = []
    scale = settings.getfloat("DEFAULT", "scale")
    jitter_filter = JitterFilter(
        threshold=settings.getfloat("Jitter Filter", "threshold") * scale,
        period=settings.getint("Jitter Filter", "period"),
    )
    moving_average_filter = MovingAverageFilter(
        period=settings.getint("DEFAULT", "moving_average_period")
    )
    root = connection.get_setup().roots[0]
    screen = Screen(root.width_in_pixels, root.height_in_pixels)
    await dbus.setup(screen, windows)
    frame_rate = settings.getfloat("DEFAULT", "frame_rate")
    Thread(
        target=handle_events,
        args=(connection, windows, screen, frame_rate),
        daemon=True,
    ).start()
    while True:
        got_frame, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        if face_delta_:
            window_delta = face_delta_
            window_delta = (window_delta[0] * scale, -window_delta[1] * scale)
            window_delta = moving_average_filter.filter(window_delta)
            window_delta = jitter_filter.filter(window_delta)
            pan(windows, window_delta)
        connection.flush()
        await asyncio.sleep(1 / frame_rate)


asyncio.run(main())
