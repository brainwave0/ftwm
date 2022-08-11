from window import Window
from xcffib import connect
from lib import register_wm, face_delta, handle_event, pan
import cv2
from os import environ
import mediapipe
face_detection = mediapipe.solutions.face_detection


connection = connect(environ['DISPLAY'])
register_wm(connection)
camera = cv2.VideoCapture(0)
windows: list[Window] = []
with face_detection.FaceDetection(model_selection=0, min_detection_confidence=0) as face_detector:
    while True:
        handle_event(connection, windows)
        _, frame = camera.read()
        face_delta_ = face_delta(face_detector, frame)
        pan(windows, (face_delta_[0], -face_delta_[1]), scale=2)
        connection.flush()
