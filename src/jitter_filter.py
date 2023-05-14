from collections import deque
from typing import Sequence
from statistics import mean


class JitterFilter:
    """
    Filters out small, random fluctuations in position.

    origin: The position it should start at.
    threshold: Minimum change in position to allow through the filter. Larger values reduce jitteriness, making the movement more sticky.
    period: How many iterations to keep track of. Larger values prevent it from getting stuck mid-movement, but increase the delay before stillness is detected.
    """

    def __init__(
        self,
        origin: tuple[float, float] = (0, 0),
        threshold: float = 56,
        period: int = 7,
    ):
        self._prevs: deque[tuple[float, float]] = deque(
            [origin], maxlen=period
        )  # last `period` recorded values
        self._anchor = origin  # reference position to stick to
        self._threshold = threshold
        self._period = period

    def _moving(self) -> bool:
        """
        Determines if the subject is moving or still. It works by summing the changes in position. If the subject is still, then it should be close to zero.
        """
        return any(sum(a - b for a, b in zip(xs, xs[1:])) > self._threshold for xs in transpose(self._prevs))

    def filter(self, other: tuple[float, float]) -> tuple[float, float]:
        self._prevs.append(other)
        if self._moving():
            self._anchor = other
        return self._anchor
