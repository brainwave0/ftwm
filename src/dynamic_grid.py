import numpy
from typing import Sequence
from .rectangle import Rectangle


class DynamicGrid:
    def __init__(self):
        self._array = numpy.array([[None]])
        self._vertical_splits = [0]
        self._horizontal_splits = [0]

    def split(self, split: int, dim: int) -> None:
        if dim == 0:
            splits = self._vertical_splits
        else:
            splits = self._horizontal_splits

        if split not in splits:
            splits.append(split)
            splits.sort()
            index = splits.index(split)
            if dim == 0:
                values = self._array[:, index - 1]
            else:
                values = self._array[index - 1]
            self._array = numpy.insert(self._array, index, values, axis=0 if dim == 1 else 1)  

    def set_range(self, rectangle: Sequence[int], obj):
        self.split(rectangle[0], 0)
        self.split(rectangle[0] + rectangle[2], 0)
        self.split(rectangle[1], 1)
        self.split(rectangle[1] + rectangle[3], 1)
        for coords in numpy.ndindex(self._array.shape):
            if self._in_range(coords, rectangle):
                self._array[coords] = obj

    def get_range(self, rectangle: Rectangle):
        return [(cell, value) for cell, value in self if cell.overlaps(rectangle)]

    def _in_range(self, cell_coords, rectangle: Sequence[int]):
        return rectangle[0] <= self._vertical_splits[cell_coords[1]] < rectangle[0] + rectangle[2] and rectangle[1] <= self._horizontal_splits[cell_coords[0]] < rectangle[1] + rectangle[3]

    def __iter__(self):
        for y in range(len(self._horizontal_splits) - 1):
            for x in range(len(self._vertical_splits) - 1):
                left = self._vertical_splits[x]
                top = self._horizontal_splits[y]
                width = self._vertical_splits[x + 1] - left
                height = self._horizontal_splits[y + 1] - top
                value = self._array[y, x]
                yield Rectangle(left, top, width, height), value

    def expand(self, top, right, bottom, left):
        if top < self._horizontal_splits[0]:
            self.split(top, 1)
        if right > self._vertical_splits[-1]:
            self.split(right, 0)
        if bottom > self._horizontal_splits[-1]:
            self.split(bottom, 1)
        if left < self._vertical_splits[0]:
            self.split(left, 0)