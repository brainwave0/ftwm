import logging
from .window import Window
import cv2
from configparser import ConfigParser
from pathlib import Path
from xdg_base_dirs import xdg_config_home
from glob import glob
from .face_tracking import get_face_detections, get_face_position
from os import makedirs
import shutil
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
from typing import cast, Optional
from .util import get_and_set_up_camera


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


async def pan_windows_with_face(state: State) -> None:
    input_size = (300, 300)
    face_detector = cv2.FaceDetectorYN_create(
        # type: ignore[attr-defined]
        "./assets/face_detection_yunet_2023mar.onnx",
        "",
        input_size,
        score_threshold=0.5,
    )
    scale = state.settings.getfloat("DEFAULT", "scale")
    camera = get_and_set_up_camera(state, face_detector)
    moving_average_filter = MovingAverageFilter(
        period=state.settings.getint("DEFAULT", "moving_average_period")
    )
    while True:
        if not state.paused:
            frame = camera.get_frame()
            if frame is not None:
                frame = cv2.resize(frame, input_size)  # type: ignore
                face_delta = get_face_position(
                    face_detector, frame
                )  # type: ignore[arg-type]
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
