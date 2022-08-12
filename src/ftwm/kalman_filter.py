from numpy import array, float64
import cv2


class KalmanFilter:
    """
    A wrapper for cv2.KalmanFilter that is set up for 2d positions.
    """

    def __init__(self) -> None:
        self.cv2_kalman_filter = cv2.KalmanFilter(6, 2, type=6)
        scale = 2
        dt = 0.4221
        err_stdev = 1.058635831 * scale
        acc = 1 * 2
        self.cv2_kalman_filter.transitionMatrix = array([
            [1.0, dt, 0.5 * dt**2, 0.0, 0.0, 0.0],
            [0.0, 1.0, dt, 0.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, dt, 0.5 * dt**2],
            [0.0, 0.0, 0.0, 0.0, 1.0, dt],
            [0.0, 0.0, 0.0, 0.0, 0.0, 1.0],
        ], float64)
        self.cv2_kalman_filter.statePre = array(
            [[0.0], [0.0], [0.0], [0.0], [0.0], [0.0]], float64)
        self.cv2_kalman_filter.measurementMatrix = array([
            [1.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0, 0.0, 0.0],
        ], float64)
        self.cv2_kalman_filter.processNoiseCov = array([
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
        ], float64)
        self.cv2_kalman_filter.measurementNoiseCov = array([
            [err_stdev**2, 0.0],
            [0.0, err_stdev**2],
        ], float64)

    def correct(self, value: tuple[int, int]) -> tuple[int, int]:
        corrected = self.cv2_kalman_filter.correct(
            array([[float(value[0])], [float(value[1])]], float64))
        self.cv2_kalman_filter.predict()
        return int(corrected[0][0]), int(corrected[3][0])
