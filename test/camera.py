from unittest.mock import Mock
from src.camera import Camera


def test_get_frame():
    camera = Camera.__new__(Camera)

    camera._frame = None
    frame = camera.get_frame()
    assert camera.get_frame() is None

    camera._frame = "foo"
    assert camera.get_frame() == "foo"

    camera._frame = None
    assert camera.get_frame() == "foo"

    camera._frame = "bar"
    assert camera.get_frame == "bar"

def test_set_frame():
    camera = Camera.__new__(Camera)
    camera._video_capture = Mock()

    camera._frame = None
    camera._video_capture.read.return_value = (True, "foo")
    camera._set_frame()
    assert camera._frame is None

    camera._frame = "bar"
    camera._video_capture.read.return_value = (True, "foo")
    camera._set_frame()
    assert camera._frame is "bar"

    camera._frame = None
    camera._video_capture.read.return_value = (False, None)
    with raises(RuntimeError):
        camera._set_frame()
