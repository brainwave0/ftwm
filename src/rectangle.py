from __future__ import annotations


class Rectangle:
    def __init__(
        self, left: float = 0, top: float = 0, width: float = 0, height: float = 0
    ) -> None:
        assert width >= 0 and height >= 0
        self._top = top
        self._left = left
        self._width = width
        self._height = height

    def get_top(self) -> float:
        return self._top

    def set_top(self, other: float) -> None:
        self._top = other

    def get_left(self) -> float:
        return self._left

    def set_left(self, other: float) -> None:
        self._left = other

    def get_width(self) -> float:
        return self._width

    def set_width(self, other: float) -> None:
        self._width = other

    def get_height(self) -> float:
        return self._height

    def set_height(self, other: float) -> None:
        self._height = other

    def get_right(self) -> float:
        return self.get_left() + self.get_width()

    def set_right(self, other: float) -> None:
        self.set_left(self.get_left() + (self.get_left() - other))

    def get_bottom(self) -> float:
        return self.get_top() + self.get_height()

    def set_bottom(self, other: float) -> None:
        self.set_top(self.get_top() + (self.get_top() - other))

    def get_top_center(self) -> tuple[float, float]:
        return self.get_left() + self.get_width() / 2, self.get_top()

    def set_top_center(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width() / 2)
        self.set_top(other[1])

    def get_right_center(self) -> tuple[float, float]:
        return (
            self.get_left() + self.get_width(),
            self.get_top() + self.get_height() / 2,
        )

    def set_right_center(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width())
        self.set_top(other[1] - self.get_height() / 2)

    def get_bottom_center(self) -> tuple[float, float]:
        return (
            self.get_left() + self.get_width() / 2,
            self.get_top() + self.get_height(),
        )

    def set_bottom_center(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width() / 2)
        self.set_top(other[1] - self.get_height())

    def get_center(self) -> tuple[float, float]:
        return (
            self.get_left() + self.get_width() / 2,
            self.get_top() + self.get_height() / 2,
        )

    def set_center(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width() / 2)
        self.set_top(other[1] - self.get_height() / 2)

    def get_size(self) -> tuple[float, float]:
        return self.get_width(), self.get_height()

    def set_size(self, other: tuple[float, float]) -> None:
        self.set_width(other[0])
        self.set_height(other[1])

    def get_top_left(self) -> tuple[float, float]:
        return self.get_left(), self.get_top()

    def set_top_left(self, other: tuple[float, float]) -> None:
        self.set_left(other[0])
        self.set_top(other[1])

    def get_position(self) -> tuple[float, float]:
        return self.get_top_left()

    def set_position(self, other: tuple[float, float]) -> None:
        self.set_top_left(other)

    def get_top_right(self) -> tuple[float, float]:
        return self.get_left() + self.get_width(), self.get_top()

    def set_top_right(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width())
        self.set_top(other[1])

    def get_bottom_right(self) -> tuple[float, float]:
        return self.get_left() + self.get_width(), self.get_top() + self.get_height()

    def set_bottom_right(self, other: tuple[float, float]) -> None:
        self.set_left(other[0] - self.get_width())
        self.set_top(other[1] - self.get_height())

    def get_bottom_left(self) -> tuple[float, float]:
        return self.get_left(), self.get_top() + self.get_height()

    def set_bottom_left(self, other: tuple[float, float]) -> None:
        self.set_left(other[0])
        self.set_top(other[1] - self.get_height())

    def get_left_center(self) -> tuple[float, float]:
        return self.get_left(), self.get_top() + self.get_height() / 2

    def set_left_center(self, other: tuple[float, float]) -> None:
        self.set_left(other[0])
        self.set_top(other[1] - self.get_height() / 2)

    def as_list(self) -> list[float]:
        return [self.get_left(), self.get_top(), self.get_width(), self.get_height()]

    def __add__(self, other: Rectangle) -> Rectangle:
        result = Rectangle()
        result.set_left(min(self.get_left(), other.get_left()))
        result.set_top(min(self.get_top(), other.get_top()))
        result.set_width(max(self.get_right(), other.get_right()) - result.get_left())
        result.set_height(max(self.get_bottom(), other.get_bottom()) - result.get_top())
        return result

    def overlaps(self, other: Rectangle) -> bool:
        return (
            self.get_left() < other.get_right()
            and other.get_left() < self.get_right()
            and self.get_top() < other.get_bottom()
            and other.get_top() < self.get_bottom()
        )

    def __contains__(self, other: Rectangle) -> bool:
        return (
            self.get_left() <= other.get_left() <= self.get_right()
            and self.get_left() <= other.get_right() <= self.get_right()
            and self.get_top() <= other.get_top() <= self.get_bottom()
            and self.get_top() <= other.get_bottom() <= self.get_bottom()
        )

    def area(self) -> float:
        return self.get_width() * self.get_height()

    def __repr__(self) -> str:
        return f"Rectangle(left={self.get_left()}, top={self.get_top()}, width={self.get_width()}, height={self.get_height()})"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Rectangle):
            return self.as_list() == other.as_list()
        else:
            return NotImplemented
