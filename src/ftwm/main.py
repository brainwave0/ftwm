from .kalman_filter import KalmanFilter
from .window import Window
from xcffib import connect
from .lib import register_wm, face_delta, handle_event, pan
import cv2
from os import environ
import mediapipe
face_detection = mediapipe.solutions.face_detection


connection = connect(environ['DISPLAY'])
register_wm(connection)
camera = cv2.VideoCapture(0)
windows: list[Window] = []
kalman_filter = KalmanFilter()
with face_detection.FaceDetection(model_selection=0, min_detection_confidence=0) as face_detector:
    while True:
        handle_event(connection, windows)
        _, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        if face_delta_:
            scale = 2
            window_delta = kalman_filter.correct((face_delta_[0] *
                                                  scale, -face_delta_[1] * scale))
            pan(windows, window_delta)
        connection.flush()
