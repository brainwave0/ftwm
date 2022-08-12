from .window import Window
from .event_handlers import handle_map_request
import cv2
from xcffib import Connection
from typing import Iterable, Optional
from xcffib.xproto import CW, EventMask, ConfigWindow, MapRequestEvent
import mediapipe
face_detection = mediapipe.solutions.face_detection


def pan(windows: Iterable[Window], delta: tuple[int, int], scale: float = 1) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in windows:
        window.position = (
            int(window.virtual_position[0] + delta[0] * scale), int(window.virtual_position[1] + delta[1] * scale))


def register_wm(connection: Connection) -> None:
    root_id = connection.get_setup().roots[0].root
    connection.core.ChangeWindowAttributes(root_id, CW.EventMask, [
                                           EventMask.PropertyChange | EventMask.StructureNotify | EventMask.SubstructureNotify | EventMask.SubstructureRedirect])


def relative_face_area(detection: mediapipe.framework.formats.detection_pb2.Detection) -> float:
    box = detection.location_data.relative_bounding_box
    return box.width * box.height


def face_delta(face_detector: mediapipe.solutions.face_detection.FaceDetection, image: cv2.Mat) -> Optional[tuple[int, int]]:
    """
    Gets the nose position relative to the center of the camera frame.
    """
    center = (int(image.shape[1] / 2), int(image.shape[0] / 2))
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    detections = face_detector.process(image).detections
    if detections:
        closest: mediapipe.framework.formats.detection_pb2.Detection = max(
            detections, key=lambda x: relative_face_area(x))
        point = face_detection.get_key_point(
            closest, face_detection.FaceKeyPoint.NOSE_TIP)
        return (int(point.x * image.shape[1] - center[0]), int(point.y * image.shape[0] - center[1]))
    else:
        return None


def handle_event(connection: Connection, windows: list[Window]) -> None:
    event = connection.poll_for_event()
    if isinstance(event, MapRequestEvent):
        handle_map_request(connection, event, windows)
