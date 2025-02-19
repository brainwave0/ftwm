import logging
from .window import Window
import cv2  # type: ignore[import-not-found]
from configparser import ConfigParser
from pathlib import Path
from xdg_base_dirs import xdg_config_home  # type: ignore[import-not-found]
from glob import glob
from .face_tracking import get_face_detections, get_face_delta
from os import makedirs
import shutil
from .moving_average_filter import MovingAverageFilter
import asyncio
from .state import State
from .camera import Camera
from wlroots.wlr_types import ( # type: ignore[attr-defined]
    Surface,
    SceneNodeType,
    SceneBuffer,
    SceneSurface,
    SceneTree,
)
from typing import cast


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


def get_settings() -> ConfigParser:
    source_directory = Path(__file__).resolve().parent
    settings_file_path = xdg_config_home() / "ftwm/settings.ini"
    defaults = source_directory.parent / "settings.ini"
    if not settings_file_path.is_file():
        makedirs(settings_file_path.parent, exist_ok=True)
        shutil.copy(defaults, settings_file_path)
    settings = ConfigParser()
    settings.read(defaults, settings_file_path)
    return settings


def auto_camera_index() -> Optional[cv2.VideoCapture]:
    for index in sorted(
        int(device.replace("/dev/video", "")) for device in glob("/dev/video*")
    ):
        camera = cv2.VideoCapture(index)
        _, frame = camera.read()
        if frame is not None:
            return index
        else:
            camera.release()
            return None


def get_and_set_up_camera(
    state: State, face_detector: cv2.FaceDetectorYN
) -> cv2.VideoCapture:
    fps = state.settings.getint("Camera", "fps")
    if (
        "capture_width" in state.settings["Camera"]
        and "capture_height" in state.settings["Camera"]
    ):
        size = (
            state.settings.getint("Camera", "capture_width"),
            state.settings.getint("Camera", "capture_height"),
        )
    else:
        size = None
    camera = (
        Camera(state.settings.getint("Camera", "index"), size, fps)
        if "index" in state.settings["Camera"]
        else Camera(auto_camera_index(), size, fps)
    )
    return camera


async def pan_windows_with_face(state: State) -> None:
    input_size = (300, 300)
    face_detector = cv2.FaceDetectorYN_create('./assets/face_detection_yunet_2023mar.onnx', "", input_size, score_threshold=0.5)
    scale = state.settings.getfloat("DEFAULT", "scale")
    camera = get_and_set_up_camera(state, face_detector)
    moving_average_filter = MovingAverageFilter(
        period=state.settings.getint("DEFAULT", "moving_average_period")
    )
    while True:
        if not state.paused:
            frame = camera.get_frame()
            if frame is not None:
                frame = cv2.resize(frame, input_size)
                face_delta = get_face_delta(face_detector, frame)
                if face_delta:
                    window_delta = face_delta
                    window_delta = moving_average_filter.filter(window_delta)
                    window_delta = (window_delta[0] * scale, -window_delta[1] * scale)
                    pan(state, window_delta)
        await asyncio.sleep(1 / state.settings.getfloat("DEFAULT", "frame_rate"))


def delay_resume_panning(state: State) -> None:
    async def helper(state: State) -> None:
        await asyncio.sleep(
            state.settings.getfloat("DEFAULT", "panning_resume_delay") / 1000
        )
        state.paused = False

    if "delay_resume_panning" in state.tasks:
        state.tasks["delay_resume_panning"].cancel()
    state.tasks["delay_resume_panning"] = asyncio.create_task(helper(state))



