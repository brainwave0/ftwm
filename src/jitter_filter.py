from collections import deque
from typing import Sequence


class JitterFilter:
    """
    Filters out small, random fluctuations in position.

    origin: The position it should start at.
    threshold: Minimum change in position to allow through the filter. Controls the 'stickiness' of the output.
    period: How many iterations to keep track of. Larger values prevent it from getting stuck mid-movement, but increase the delay before stillness is detected.
    """

    def __init__(self, origin: tuple[int, int] = (0, 0), threshold: int = 48, period: int = 6):
        self._prevs: deque[tuple[int, int]] = deque(
            [origin])  # last [period] recorded values
        self._anchor = origin  # reference position to stick to
        self._threshold = threshold
        self._period = period

    def _moving(self, xs: Sequence[int]) -> bool:
        """
        Determines if the subject is moving or still. It works by summing the changes and comparing the absolute value of the sum to the threshold.
        """
        return len(xs) > 1 and abs(sum(a - b for a, b in zip(xs, xs[1:]))) > self._threshold

    def filter(self, other: tuple[int, int]) -> tuple[int, int]:
        # update self._prevs
        self._prevs.appendleft(other)
        if len(self._prevs) > self._period:
            self._prevs.pop()

        if self._moving([i[0] for i in self._prevs]) or self._moving([i[1] for i in self._prevs]):
            self._anchor = other
            return other
        else:
            return self._anchor
