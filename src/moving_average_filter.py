from statistics import mean, median
from collections import deque


class MovingAverageFilter:
    def __init__(self, period: int = 2):
        self.previous_positions = deque([(0, 0)], maxlen=period)

    def filter(self, value: tuple[float, float]) -> tuple[float, float]:
        self.previous_positions.append(value)
        return mean(i[0] for i in self.previous_positions), mean(
            i[1] for i in self.previous_positions
        )
