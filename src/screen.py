from .rectangle import Rectangle
from .dynamic_grid import DynamicGrid


class Screen(Rectangle):
    def __init__(self, width, height, **kwargs):
        super().__init__(**kwargs)
        self.grid = DynamicGrid()
        self.width = width
        self.height = height
