from functools import reduce
from typing import Optional, Sequence

import cv2
import mediapipe
from mediapipe.framework.formats.detection_pb2 import Detection
import logging

face_detection = mediapipe.solutions.face_detection


def relative_face_area(detection: Detection) -> float:
    """
    Calculates the area of the face relative to the size of the screen. Used for finding the biggest face which is assumed to be the closest.
    """
    box = detection.location_data.relative_bounding_box
    return box.width * box.height


def average_point(image: cv2.Mat, detection: Detection) -> tuple[float, float]:
    """
    Averages the detected points for each feature of the face, including the center of the bounding box. This helps to reduce jitter.
    """
    points = [
        face_detection.get_key_point(detection, i) for i in face_detection.FaceKeyPoint
    ]
    points = [(point.x * image.shape[1], point.y * image.shape[0]) for point in points]
    box = detection.location_data.relative_bounding_box
    box_center = (
        (box.xmin + box.width / 2) * image.shape[1],
        (box.ymin + box.height / 2) * image.shape[0],
    )
    points.append(box_center)
    point = reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), points)
    return point[0] / len(points), point[1] / len(points)


def face_detections(face_detector, image: cv2.Mat) -> Optional[Sequence[Detection]]:
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    detections = face_detector.process(image).detections
    return detections


# noinspection PyUnresolvedReferences
def face_delta(face_detector, image: cv2.Mat) -> Optional[tuple[float, float]]:
    """
    Gets the nose position relative to the center of the camera frame.
    """
    center = (image.shape[1] / 2, image.shape[0] / 2)
    detections = face_detections(face_detector, image)
    if detections:
        closest: mediapipe.framework.formats.detection_pb2.Detection = max(
            detections, key=lambda x: relative_face_area(x)
        )
        average_point_ = average_point(image, closest)
        return average_point_[0] - center[0], average_point_[1] - center[1]
    else:
        return None
