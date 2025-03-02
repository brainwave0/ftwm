from numpy import array, float64
from .window import Window
import cv2
from xdg_base_dirs import xdg_config_home
from .face_tracking import FaceTracker
from .moving_average_filter import MovingAverageFilter
import asyncio
from .state import State
from .camera import Camera
from wlroots.wlr_types import (  # type: ignore[attr-defined]
    Surface,
    SceneNodeType,
    SceneBuffer,
    SceneSurface,
    SceneTree,
)
from .util import get_and_set_up_camera
import math


def pan(state: State, delta: tuple[float, float]) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    """
    for window in state.windows:
        window.position = (
            int(window.virtual.position[0] + delta[0]),
            int(window.virtual.position[1] + delta[1]),
        )


async def pan_windows_with_face(state: State) -> None:
    scale = state.settings.getfloat("DEFAULT", "scale")
    moving_average_filter = MovingAverageFilter(
        period=state.settings.getint("DEFAULT", "moving_average_period")
    )
    frame_rate = state.settings.getfloat("DEFAULT", "frame_rate")
    detection_rate = 1 / state.settings.getfloat("DEFAULT", "seconds_per_detection")
    face_tracker = FaceTracker((640, 480), detection_rate, frame_rate, 0.5, "./assets/face_detection_yunet_2023mar.onnx", 96)
    camera = get_and_set_up_camera(state)
    while True:
        if not state.paused:
            frame = camera.get_frame()
            if frame is not None:
                point = face_tracker.get_point(frame)
                if point is not None:
                    frame_center = array([frame.shape[1], frame.shape[0]], dtype=float64) / 2  # type: ignore
                    window_delta = frame_center - array(point, dtype=float64)
                    window_delta = moving_average_filter.filter(window_delta)
                    window_delta *= array([scale], dtype=float64)
                    window_delta *= array([-1, 1], dtype=float64)
                    pan(state, tuple(window_delta))
        await asyncio.sleep(1 / frame_rate)


def delay_resume_panning(state: State) -> None:
    async def helper(state: State) -> None:
        await asyncio.sleep(
            state.settings.getfloat("DEFAULT", "panning_resume_delay") / 1000
        )
        state.paused = False

    if "delay_resume_panning" in state.tasks:
        state.tasks["delay_resume_panning"].cancel()
    loop = asyncio.get_running_loop()
    state.tasks["delay_resume_panning"] = loop.create_task(helper(state))
