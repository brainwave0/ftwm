import sys
import logging
from functools import reduce
from typing import Optional, Sequence
from numpy.typing import ArrayLike
import numpy

import cv2  # type: ignore[import-not-found]


def get_relative_face_area(detection: ArrayLike) -> float:
    """
    Calculates the area of the face relative to the size of the screen. Used for finding the biggest face which is assumed to be the closest.
    """
    width, height = detection[2:4]
    return width * height


def get_average_point(image: cv2.Mat, detection: ArrayLike) -> tuple[float, float]:
    """
    Averages the detected points for each feature of the face. This helps to reduce jitter.
    """
    points = detection[0:14].reshape(-1, 2)  # convert from 1D array to pairs
    point = reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), points)  # sum
    return point[0] / len(points), point[1] / len(points)


def get_face_detections(
    face_detector: cv2.FaceDetectorYN, image: cv2.Mat
) -> Optional[Sequence[ArrayLike]]:
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    detections = face_detector.detect(image)
    return detections  # type: ignore[no-any-return]


# noinspection PyUnresolvedReferences
def get_face_position(
    face_detector: cv2.FaceDetectorYN, image: cv2.Mat
) -> Optional[tuple[float, float]]:
    center = (image.shape[1] / 2, image.shape[0] / 2)
    detections = get_face_detections(face_detector, image)[1]
    if detections is not None:
        closest: ArrayLike = max(
            detections, key=lambda x: get_relative_face_area(x)
        )
        average_point = get_average_point(image, closest)
        return average_point[0] - center[0], average_point[1] - center[1]
    else:
        return None
