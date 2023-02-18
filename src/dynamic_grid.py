from typing import Any, Iterator

import numpy

from .rectangle import Rectangle


class DynamicGrid:
    """
    This class represents a two-dimensional grid. Because iterating through each cell in a grid can be expensive, the
    search space is reduced by splitting the grid around the areas of interest.
    """

    def __init__(self) -> None:
        self._array = numpy.array([[None, None], [None, None]])
        self._vertical_splits: list[float] = []
        self._horizontal_splits: list[float] = []

    def split(self, split: float, dim: int) -> None:
        """
        Split the grid at the given index on the given axis. The grid is split vertically on the X axis, and
        horizontally on the Y axis. This operation is idempotent.
        """
        assert dim in (0, 1)
        if dim == 0:
            splits = self._vertical_splits
        else:
            splits = self._horizontal_splits

        if split not in splits:
            splits.append(split)
            if len(self._vertical_splits) > 1 and len(self._horizontal_splits) > 1:
                # there are enough splits to surround at least one cell

                splits.sort()
                index = splits.index(split)

                # Splitting creates a new row or column which must be populated with the values of the row or column
                # that was split.
                if dim == 0:
                    values = self._array[:, index - 1]
                else:
                    values = self._array[index - 1]

                self._array = numpy.insert(
                    self._array, index, values, axis=0 if dim == 1 else 1
                )

    def set_range(self, rectangle: Rectangle, obj: Any) -> None:
        """
        Set the area given by `rectangle` to contain `obj`. The grid is split at each edge of the rectangle, and `obj`
        copied over the cells contained in it.
        """
        self.split(rectangle.left, 0)
        self.split(rectangle.right, 0)
        self.split(rectangle.top, 1)
        self.split(rectangle.bottom, 1)
        for cell, _ in self:
            if cell.overlaps(rectangle):
                self._array[
                    self._horizontal_splits.index(cell.top),
                    self._vertical_splits.index(cell.left),
                ] = obj

    def get_range(self, rectangle: Rectangle) -> list[tuple[Rectangle, Any]]:
        return [(cell, value) for cell, value in self if cell.overlaps(rectangle)]

    def __iter__(self) -> Iterator[tuple[Rectangle, Any]]:
        for y in range(len(self._horizontal_splits) - 1):
            for x in range(len(self._vertical_splits) - 1):
                left = self._vertical_splits[x]
                top = self._horizontal_splits[y]
                width = self._vertical_splits[x + 1] - left
                height = self._horizontal_splits[y + 1] - top
                value = self._array[y, x]
                yield Rectangle(left, top, width, height), value

    def expand(self, top: float, right: float, bottom: float, left: float) -> None:
        """
        Expands the grid to contain the given area.
        """
        if top < self._horizontal_splits[0]:
            self.split(top, 1)
        if right > self._vertical_splits[-1]:
            self.split(right, 0)
        if bottom > self._horizontal_splits[-1]:
            self.split(bottom, 1)
        if left < self._vertical_splits[0]:
            self.split(left, 0)
