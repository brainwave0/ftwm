from collections import deque
from typing import Sequence


class JitterFilter:
    """
    Filters out small, random fluctuations in position.

    origin: The position it should start at.
    threshold: Minimum change in position to allow through the filter. Larger values reduce jitteriness, making the movement more sticky.
    period: How many iterations to keep track of. Larger values prevent it from getting stuck mid-movement, but increase the delay before stillness is detected.
    """

    def __init__(
        self, origin: tuple[float, float] = (0, 0), threshold: float = 56, period: int = 7
    ):
        self._prevs: deque[tuple[float, float]] = deque(
            [origin], maxlen=period
        )  # last [period] recorded values
        self._anchor = origin  # reference position to stick to
        self._threshold = threshold
        self._period = period

    def _moving(self, xs: Sequence[float]) -> bool:
        """
        Determines if the subject is moving or still. It works by summing the changes in position. If the subject is still, then it should be close to zero.
        """
        return (
            len(xs) > 1
            and abs(sum(a - b for a, b in zip(xs, xs[1:]))) > self._threshold
        )

    def filter(self, other: tuple[float, float]) -> tuple[float, float]:
        self._prevs.append(other)
        if self._moving([i[0] for i in self._prevs]) or self._moving(
            [i[1] for i in self._prevs]
        ):
            self._anchor = other
            return other
        else:
            return self._anchor
