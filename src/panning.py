from numpy import array, float64
from .window import Window
import cv2
from xdg_base_dirs import xdg_config_home
from .face_tracker import FaceTracker
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


def pan(state: State, delta: tuple[float, float]) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    """
    state.window_group_tree.node.set_position(*tuple(map(int, delta)))


async def pan_windows_with_face(state: State) -> None:
    scale = state.settings.getfloat("DEFAULT", "scale")
    moving_average_filter = MovingAverageFilter(
        period=state.settings.getint("DEFAULT", "moving_average_period")
    )
    frame_rate = state.settings.getfloat("DEFAULT", "frame_rate")
    capture_size = (
        state.settings.getint("Camera", "capture_width"),
        state.settings.getint("Camera", "capture_height"),
    )
    detection_threshold = state.settings.getfloat("Face Tracker", "detection_threshold")
    tracking_area = state.settings.getint("Face Tracker", "tracking_area")
    face_tracker = FaceTracker(
        capture_size,
        detection_threshold,
        "./assets/face_detection_yunet_2023mar.onnx",
        tracking_area,
    )
    camera = get_and_set_up_camera(state)
    while True:
        if not state.paused:
            frame = await camera.get_frame()
            point = face_tracker.get_point(frame)
            if point is not None:
                frame_center = array([frame.shape[1], frame.shape[0]], dtype=float64) / 2  # type: ignore
                window_delta = frame_center - array(point, dtype=float64)
                window_delta = moving_average_filter.filter(tuple(window_delta))  # type: ignore
                window_delta *= array([scale], dtype=float64)
                window_delta *= array([-1, 1], dtype=float64)
                pan(state, window_delta)  # type: ignore[arg-type]
                state.window_delta = window_delta  # type: ignore[assignment]
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
