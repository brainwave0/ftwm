from functools import reduce
from typing import Optional, Sequence
from numpy.typing import ArrayLike
import numpy

import cv2
import math
from numpy import array, float64, float32

class FaceTracker:
    def __init__(self, detector_input_size: tuple[int, int], detection_threshold: float, model_path: str, bounding_box_size: float):
        self._detector_input_size = detector_input_size
        self._face_detector = cv2.FaceDetectorYN_create(  # type: ignore[attr-defined]
            model_path,
            "",
            detector_input_size,
            score_threshold=detection_threshold,
        )
        self._tracker: Optional[cv2.legacy.TrackerMOSSE] = None
        self._point: Optional[tuple[float, float]] = None
        self._bounding_box_size = bounding_box_size
        self.tracking_succeeded = False

        
    def _get_face_area(self, detection: ArrayLike) -> float:
        width, height = detection[2:4]  # type: ignore
        return width * height  # type: ignore


    # noinspection PyUnresolvedReferences
    def _get_detection_point(self, frame: ArrayLike) -> Optional[tuple[float, float]]:
        """
        Find the bounding box of the largest face in the frame and return its center.
        """
        detections = self._face_detector.detect(frame)[1]
        if detections is not None:
            closest: ArrayLike = max(
                detections, key=lambda x: self._get_face_area(x)
            )
            top_left, dimensions  = closest[0:14].reshape(-1, 2)[0:2]  # type: ignore
            # result = tuple(array(top_left, dtype=float64) + array(dimensions, dtype=float64) / 2)

            # nose tip
            result = tuple(array(closest[8:10], dtype=float64))  # type: ignore

            self._init_tracker(frame, result)
            return result
        return None

    def _get_tracker_point(self, frame: ArrayLike) -> Optional[tuple[float, float]]:
        if self._tracker is not None:
            success, box = self._tracker.update(frame)  # type: ignore
            if success:
                x, y, w, h = box
                result = x + w / 2, y + h / 2
                if self._in_frame(result, frame):
                    self.tracking_succeeded = True
                    return result
        self.tracking_succeeded = False
        return None

    def get_point(self, frame: ArrayLike) -> Optional[tuple[float, float]]:
        # prepare the frame
        frame_size = array([frame.shape[1], frame.shape[0]], dtype=float64)  # type: ignore
        if frame is not None:
            # frame.flags.writeable = False  # type: ignore
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)  # type: ignore
            frame = cv2.resize(frame, self._detector_input_size)  # type: ignore

            point = self._get_tracker_point(frame) or self._get_detection_point(frame)              
            if point is not None:
                self._point = tuple(array(frame_size, dtype=float64) / array(self._detector_input_size, dtype=float64) * array(point, dtype=float64))  # scale back to actual frame size
        return self._point 

    def _init_tracker(self, frame: ArrayLike, point: tuple[float, float]) -> None:
        box = cv2.boundingRect(array(self._bounding_box_points(point), dtype=float32))
        self._tracker = cv2.legacy.TrackerMOSSE.create()
        if not self._tracker.init(frame, box):  # type: ignore
            raise RuntimeError("tracker initialization failed")

    def _in_frame(self, point: tuple[float, float], frame: ArrayLike) -> bool:
        height = frame.shape[0]  # type: ignore
        width = frame.shape[1]  # type: ignore
        return self._bounding_box_size / 2 < point[0] < width - self._bounding_box_size / 2 and self._bounding_box_size / 2 < point[1] < height - self._bounding_box_size / 2  # type: ignore

    def _bounding_box_points(self, point: tuple[float, float]) -> tuple[tuple[float, float]]:
        return tuple(array(point, dtype=float32) - array(self._bounding_box_size / 2, dtype=float32)), tuple(array(point, dtype=float32) + array(self._bounding_box_size / 2, dtype=float32))  # type: ignore
