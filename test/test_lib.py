from ftwm.lib import *
from unittest.mock import Mock
from xcffib.xproto import ConfigWindow, EventMask, CW
import cv2
import mediapipe
face_detection = mediapipe.solutions.face_detection


def test_pan():
    windows = [Window(Mock(), 0, virtual_position=(0, 0))]
    pan(windows, (-1, 1), scale=2)
    assert windows[0].position == (-2, 2)

    windows = [Window(Mock(), 0, virtual_position=(1, -1))]
    pan(windows, (0, 1), scale=1)
    assert windows[0].position == (1, 0)

    windows = [Window(Mock(), 0, virtual_position=(2, -3)),
               Window(Mock(), 1, virtual_position=(2, -1))]
    pan(windows, (-2, -1), scale=2)
    assert windows[0].position == (-2, -5)
    assert windows[1].position == (-2, -3)

    windows = [Window(Mock(), 0, virtual_position=(3, -1))]
    pan(windows, (0, 0), scale=2)
    assert windows[0].position == (3, -1)


class TestWindow:
    def test_set_position(self):
        connection = Mock()
        window = Window(connection, 1)
        window.position = (-3, -2)
        connection.core.ConfigureWindow.assert_called_once_with(
            1, ConfigWindow.X | ConfigWindow.Y, [-3, -2])

        connection = Mock()
        window = Window(connection, 1)
        window.position = (1, 1)
        connection.core.ConfigureWindow.assert_called_once_with(
            1, ConfigWindow.X | ConfigWindow.Y, [1, 1])


def test_register_wm():
    connection = Mock()
    screen = Mock()
    screen.root = 123
    connection.get_setup.return_value.roots = [screen]
    register_wm(connection)
    connection.core.ChangeWindowAttribtues.assert_called_once_with(123, CW.EventMask, [
                                                                   EventMask.PropertyChange, EventMask.StructureNotify, EventMask.SubstructureNotify, EventMask.SubstructureRedirect])


def test_face_delta():
    with face_detection.FaceDetection(model_selection=0, min_detection_confidence=0) as face_detector:
        frame = cv2.imread('test/left-down.jpg')
        face_delta_ = face_delta(face_detector, frame)
        # result is within 50 pixels of the nose position
        assert abs(face_delta_[0] +
                   167) <= 50 and abs(face_delta_[1] - 67) <= 50

        frame = cv2.imread('test/nowhere.jpg')
        face_delta_ = face_delta(face_detector, frame)
        assert face_delta_ is None

        frame = cv2.imread('test/shoulder-surfing.jpg')
        face_delta_ = face_delta(face_detector, frame)
        # result is within 50 pixels of the nose position
        assert abs(face_delta_[0] +
                   65) <= 50 and abs(face_delta_[1] + 36) <= 50

        frame = cv2.imread('test/partial.jpg')
        face_delta_ = face_delta(face_detector, frame)
        assert face_delta_ is None

        frame = cv2.imread('test/rotated.jpg')
        face_delta_ = face_delta(face_detector, frame)
        # result is within 50 pixels of the nose position
        assert abs(face_delta_[0] -
                   144) <= 50 and abs(face_delta_[1] - 2) <= 50
