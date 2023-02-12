from time import perf_counter
from typing import Optional

import cv2
from numpy import array, float64


class KalmanFilter:
    """
    A wrapper for cv2.KalmanFilter that is set up for two-dimensional space.
    """

    def __init__(self, scale) -> None:
        self.cv2_kalman_filter = cv2.KalmanFilter(6, 2, type=6)
        err_stdev = scale
        self._acc = 64 * scale
        self.cv2_kalman_filter.statePre = array(
            [[0.0], [0.0], [0.0], [0.0], [0.0], [0.0]], float64
        )
        self.cv2_kalman_filter.measurementMatrix = array(
            [
                [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
            ],
            float64,
        )
        self.cv2_kalman_filter.measurementNoiseCov = array(
            [
                [err_stdev**2, 0.0],
                [0.0, err_stdev**2],
            ],
            float64,
        )
        self._prev_time: Optional[float] = None
        self._update_dt()

    def _update_dt(self) -> None:
        now = perf_counter()
        if self._prev_time is None:
            dt = 0.4221
        else:
            dt = now - self._prev_time
        self._prev_time = perf_counter()
        acc = self._acc
        self.cv2_kalman_filter.transitionMatrix = array(
            [
                [1.0, dt, 0.5 * dt**2, 0.0, 0.0, 0.0],
                [0.0, 1.0, dt, 0.0, 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
                [0.0, 0.0, 0.0, 1.0, dt, 0.5 * dt**2],
                [0.0, 0.0, 0.0, 0.0, 1.0, dt],
                [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
            ],
            float64,
        )
        self.cv2_kalman_filter.processNoiseCov = array(
            [
                [
                    acc**2 * dt**4 / 4,
                    acc**2 * dt**3 / 2,
                    acc**2 * dt**2 / 2,
                    0.0,
                    0.0,
                    0.0,
                ],
                [
                    acc**2 * dt**3 / 2,
                    acc**2 * dt**2,
                    acc**2 * dt,
                    0.0,
                    0.0,
                    0.0,
                ],
                [
                    acc**2 * dt**2 / 2,
                    acc**2 * dt,
                    acc**2 * 1.0,
                    0.0,
                    0.0,
                    0.0,
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    acc**2 * dt**4 / 4,
                    acc**2 * dt**3 / 2,
                    acc**2 * dt**2 / 2,
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    acc**2 * dt**3 / 2,
                    acc**2 * dt**2,
                    acc**2 * dt,
                ],
                [
                    0.0,
                    0.0,
                    0.0,
                    acc**2 * dt**2 / 2,
                    acc**2 * dt,
                    acc**2 * 1.0,
                ],
            ],
            float64,
        )

    def correct(self, value: tuple[int, int]) -> tuple[int, int]:
        self._update_dt()
        corrected = self.cv2_kalman_filter.correct(
            array([[float(value[0])], [float(value[1])]], float64)
        )
        self.cv2_kalman_filter.predict()
        return corrected[0][0], corrected[3][0]
