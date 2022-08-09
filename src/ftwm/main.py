from xcffib import connect
from lib import register_wm, face_position
import cv2


def main() -> None:
    connection = connect(':0')
    register_wm(connection)

    camera = cv2.VideoCapture(0)
    _, frame = camera.read()
    face_position_ = face_position(frame)
