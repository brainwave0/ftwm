from numpy import array
from .kalman_filter import KalmanFilter
from .jitter_filter import JitterFilter
from .screen import Screen
from .window import Window
from xcffib import connect
from .lib import register_wm, face_delta, handle_event, pan
import cv2
from os import environ
import mediapipe
face_detection = mediapipe.solutions.face_detection


connection = connect(environ['DISPLAY'])
print(environ['DISPLAY'])
register_wm(connection)
camera = cv2.VideoCapture(0)
windows: list[Window] = []
kalman_filter = KalmanFilter()
jitter_filter = JitterFilter()
root = connection.get_setup().roots[0]
screen = Screen(root.width_in_pixels, root.height_in_pixels)
with face_detection.FaceDetection(model_selection=0, min_detection_confidence=0) as face_detector:
    while True:
        handle_event(connection, windows, screen)
        _, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        if face_delta_:
            scale = 3
            window_delta = kalman_filter.correct((face_delta_[0] *
                                                  scale, -face_delta_[1] * scale))
            window_delta = jitter_filter.filter(window_delta)
            pan(windows, window_delta)
        connection.flush()
