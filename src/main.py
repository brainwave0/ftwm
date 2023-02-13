import asyncio
from argparse import ArgumentParser
from os import environ

import cv2
from mediapipe.python.solutions.face_detection import FaceDetection
from xcffib import connect

from .event import handle_event
from .face_tracking import face_delta, face_detections
from .jitter_filter import JitterFilter
from .kalman_filter import KalmanFilter
from .misc import register_wm, pan
from .screen import Screen
from .window import Window
from threading import Thread
import logging
from glob import glob
import time
import src.dbus as dbus


def handle_events(connection, windows, screen):
    while True:
        handle_event(connection, windows, screen)
        time.sleep(1 / 60)


def automatically_select_camera(face_detector):
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
    argument_parser = ArgumentParser()
    argument_parser.add_argument("--camera", type=int)
    arguments = argument_parser.parse_args()

    connection = connect(environ["DISPLAY"])
    register_wm(connection)
    face_detector = FaceDetection(model_selection=0, min_detection_confidence=0)
    camera = (
        cv2.VideoCapture(arguments.camera)
        if arguments.camera is not None
        else automatically_select_camera(face_detector)
    )
    camera.set(cv2.CAP_PROP_FPS, 60)
    windows: list[Window] = []
    kalman_filter = KalmanFilter()
    jitter_filter = JitterFilter(threshold=8, period=5)
    root = connection.get_setup().roots[0]
    screen = Screen(root.width_in_pixels, root.height_in_pixels)
    await dbus.setup(screen, windows)
    Thread(
        target=handle_events, args=(connection, windows, screen), daemon=True
    ).start()
    while True:
        got_frame, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        if face_delta_:
            window_delta = (face_delta_[0], -face_delta_[1])
            window_delta = kalman_filter.correct(window_delta)
            window_delta = jitter_filter.filter(window_delta)
            pan(windows, window_delta, scale=16)
        connection.flush()
        await asyncio.sleep(1 / 60)


asyncio.run(main())
