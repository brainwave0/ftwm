from .dynamic_grid import DynamicGrid
from .rectangle import Rectangle


class Screen:
    def __init__(self, width: float, height: float):
        assert width >= 0 and height >= 0
        self.grid = DynamicGrid()
        self.geometry = Rectangle(0, 0, width, height)
