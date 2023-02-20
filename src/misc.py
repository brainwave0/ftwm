
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
from .face_tracking import get_face_detections, get_face_delta
from os import makedirs
import shutil
from .jitter_filter import JitterFilter
from .moving_average_filter import MovingAverageFilter
import asyncio
from mediapipe.python.solutions.face_detection import FaceDetection  # type: ignore[import]
from .state import State
from .camera import Camera


def pan(state: State, delta: tuple[float, float]) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in state.windows:
        window.position = (
            int(window.virtual.position[0] + delta[0]),
            int(window.virtual.position[1] + delta[1]),
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


def auto_camera_index(face_detector: FaceDetection) -> cv2.VideoCapture:
    for index in sorted(
        int(device.replace("/dev/video", "")) for device in glob("/dev/video*")
    ):
        camera = cv2.VideoCapture(index)
        _, frame = camera.read()
        if frame is not None:
            detections = get_face_detections(face_detector, frame)
            if detections:
                camera.release()
                return index
        camera.release()
    return None


def get_and_set_up_camera(
    state: State, face_detector: FaceDetection
) -> cv2.VideoCapture:
    fps = state.settings.getint("Camera", "fps")
    if (
        "capture_width" in state.settings["Camera"]
        and "capture_height" in state.settings["Camera"]
    ):
        size = (state.settings.getint("Camera", "capture_width"), state.settings.getint("Camera", "capture_height"))
    else:
        size = None
    camera = (
        Camera(state.settings.getint("Camera", "index"), size, fps)
        if "index" in state.settings["Camera"]
        else Camera(auto_camera_index(face_detector), size, fps)
    )
    return camera


async def pan_windows_with_face(state: State) -> None:
    face_detector = FaceDetection(model_selection=0, min_detection_confidence=0)
    scale = state.settings.getfloat("DEFAULT", "scale")
    camera = get_and_set_up_camera(state, face_detector)
    jitter_filter = JitterFilter(
        threshold=state.settings.getfloat("Jitter Filter", "threshold") * scale,
        period=state.settings.getint("Jitter Filter", "period"),
    )
    moving_average_filter = MovingAverageFilter(
        period=state.settings.getint("DEFAULT", "moving_average_period")
    )
    while True:
        frame = camera.get_frame()
        if frame is not None:
            face_delta = get_face_delta(face_detector, frame)
            if face_delta:
                window_delta = face_delta
                window_delta = (window_delta[0] * scale, -window_delta[1] * scale)
                window_delta = moving_average_filter.filter(window_delta)
                window_delta = jitter_filter.filter(window_delta)
                pan(state, window_delta)
                state.connection.flush()
        await asyncio.sleep(1 / state.settings.getfloat("DEFAULT", "frame_rate"))
