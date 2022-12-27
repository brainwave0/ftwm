import asyncio
from os import environ

import cv2
from mediapipe.python.solutions.face_detection import FaceDetection
from xcffib import connect

from . import hooks, hook_modules
from .jitter_filter import JitterFilter
from .kalman_filter import KalmanFilter
from .misc import register_wm, pan
from .screen import Screen
from .window import Window
from .face_tracking import face_delta
from .handle_event import handle_event


async def main() -> None:
    hook_modules.init()
    connection = connect(environ['DISPLAY'])
    register_wm(connection)
    camera = cv2.VideoCapture(0)
    camera.set(cv2.CAP_PROP_FPS, 60)
    windows: list[Window] = []
    scale = 8
    kalman_filter = KalmanFilter(scale)
    jitter_filter = JitterFilter(threshold=(8 - 4 + 2 - 1 - 2 + 1 + 2 + 4 - 2 + 1 - 1 + 1) * scale,
                                 period=(8 - 4 + 2 - 1))
    root = connection.get_setup().roots[0]
    screen = Screen(root.width_in_pixels, root.height_in_pixels)
    await hooks.main_initializing.fire_async(screen, windows)
    face_detector = FaceDetection(model_selection=0, min_detection_confidence=0)
    while True:
        handle_event(connection, windows, screen)
        got_frame, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        if face_delta_:
            window_delta = (face_delta_[0] * scale, -face_delta_[1] * scale)
            window_delta = kalman_filter.correct(window_delta)
            window_delta = jitter_filter.filter(window_delta)
            pan(windows, window_delta)
        connection.flush()
        await asyncio.sleep(0)


asyncio.run(main())
