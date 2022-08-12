from ftwm.kalman_filter import KalmanFilter
from pytest import approx


def test_kalman_filter():
    filter = KalmanFilter()

    value = (0, 0)
    assert filter.correct(value) == approx(value, abs=50)

    value = (-10, -10)
    assert filter.correct(value) == approx(value, abs=50)

    value = (-20, -20)
    assert filter.correct(value) == approx(value, abs=50)
