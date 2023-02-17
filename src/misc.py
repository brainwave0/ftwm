from typing import Iterable

import mediapipe  # type: ignore[import]
from xcffib import Connection  # type: ignore[import]
from xcffib.xproto import (  # type: ignore[import]
    CW,
    EventMask,
)

from .window import Window
import cv2  # type: ignore[import]
from configparser import ConfigParser
from pathlib import Path
from xdg import xdg_config_home  # type: ignore[import]
from glob import glob
from .face_tracking import face_detections, get_face_delta
from os import makedirs
import shutil
from .jitter_filter import JitterFilter
from .moving_average_filter import MovingAverageFilter
import asyncio
from mediapipe.python.solutions.face_detection import FaceDetection  # type: ignore[import]


def pan(
    windows: Iterable[Window], delta: tuple[float, float], scale: float = 1
) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in windows:
        window.position = (
            int(window.virtual.position[0] + delta[0] * scale),
            int(window.virtual.position[1] + delta[1] * scale),
        )


def register_wm(connection: Connection) -> None:
    root_id = connection.get_setup().roots[0].root
    connection.core.ChangeWindowAttributes(
        root_id,
        CW.EventMask,
        [EventMask.SubstructureRedirect | EventMask.SubstructureNotify],
    )


def get_settings() -> ConfigParser:
    source_directory = Path(__file__).resolve().parent
    settings_file_path = xdg_config_home() / "ftwm/settings.ini"
    if not settings_file_path.is_file():
        makedirs(settings_file_path.parent, exist_ok=True)
        shutil.copy(source_directory.parent / "settings.ini", settings_file_path)
    settings = ConfigParser()
    settings.read(settings_file_path)
    return settings


def automatically_select_camera(face_detector: FaceDetection) -> cv2.VideoCapture:
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


def get_and_set_up_camera(
    settings: ConfigParser, face_detector: FaceDetection
) -> cv2.VideoCapture:
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
    return camera


async def pan_windows_with_face(
    connection: Connection,
    windows: list[Window],
    settings: ConfigParser,
    face_detector: FaceDetection,
) -> None:
    scale = settings.getfloat("DEFAULT", "scale")
    camera = get_and_set_up_camera(settings, face_detector)
    jitter_filter = JitterFilter(
        threshold=settings.getfloat("Jitter Filter", "threshold") * scale,
        period=settings.getint("Jitter Filter", "period"),
    )
    moving_average_filter = MovingAverageFilter(
        period=settings.getint("DEFAULT", "moving_average_period")
    )
    while True:
        got_frame, frame = camera.read()
        face_delta = get_face_delta(face_detector, frame)
        if face_delta:
            window_delta = face_delta
            window_delta = (window_delta[0] * scale, -window_delta[1] * scale)
            window_delta = moving_average_filter.filter(window_delta)
            window_delta = jitter_filter.filter(window_delta)
            pan(windows, window_delta)
        connection.flush()
        await asyncio.sleep(1 / settings.getfloat("DEFAULT", "frame_rate"))
