from operator import add
from typing import Tuple, Iterable


class Window:
    def __init__(self, position: Tuple[int, int] = (0, 0)):
        self.position = position


def pan(windows: Iterable[Window], delta: Tuple[int, int], scale: float = 1) -> None:
    for window in windows:
        tuple(map(add, window.position, delta))
