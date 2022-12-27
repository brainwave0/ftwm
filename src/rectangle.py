

class Rectangle:
    def __init__(self, left: float = 0, top: float = 0, width: float = 0, height: float = 0) -> None:
        assert width >= 0 and height >= 0
        self.top = top
        self.left = left
        self.width = width
        self.height = height

    @property
    def right(self) -> float:
        return self.left + self.width

    @right.setter
    def right(self, other: float) -> None:
        self.left += self.left - other

    @property
    def bottom(self) -> float:
        return self.top + self.height

    @bottom.setter
    def bottom(self, other: float) -> None:
        self.top += self.top - other

    @property
    def top_center(self) -> tuple[float, float]:
        return self.left + self.width / 2, self.top

    @top_center.setter
    def top_center(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width / 2
        self.top = other[1]

    @property
    def right_center(self) -> tuple[float, float]:
        return self.left + self.width, self.top + self.height / 2

    @right_center.setter
    def right_center(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width
        self.top = other[1] - self.height / 2

    @property
    def bottom_center(self) -> tuple[float, float]:
        return self.left + self.width / 2, self.top + self.height

    @bottom_center.setter
    def bottom_center(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width / 2
        self.top = other[1] - self.height

    @property
    def center(self):
        return self.left + self.width / 2, self.top + self.height / 2

    @center.setter
    def center(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width / 2
        self.top = other[1] - self.height / 2

    @property
    def size(self) -> tuple[float, float]:
        return self.width, self.height

    @size.setter
    def size(self, other: tuple[float, float]) -> None:
        self.width = other[0]
        self.height = other[1]

    @property
    def top_left(self) -> tuple[float, float]:
        return self.left, self.top

    @top_left.setter
    def top_left(self, other: tuple[float, float]) -> None:
        self.left = other[0]
        self.top = other[1]

    @property
    def position(self) -> tuple[float, float]:
        return self.top_left

    @position.setter
    def position(self, other: tuple[float, float]) -> None:
        self.top_left = other

    @property
    def top_right(self) -> tuple[float, float]:
        return self.left + self.width, self.top

    @top_right.setter
    def top_right(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width
        self.top = other[1]

    @property
    def bottom_right(self) -> tuple[float, float]:
        return self.left + self.width, self.top + self.height

    @bottom_right.setter
    def bottom_right(self, other: tuple[float, float]) -> None:
        self.left = other[0] - self.width
        self.top = other[1] - self.height

    @property
    def bottom_left(self) -> tuple[float, float]:
        return self.left, self.top + self.height

    @bottom_left.setter
    def bottom_left(self, other: tuple[float, float]) -> None:
        self.left = other[0]
        self.top = other[1] - self.height

    @property
    def left_center(self) -> tuple[float, float]:
        return self.left, self.top + self.height / 2

    @left_center.setter
    def left_center(self, other: tuple[float, float]) -> None:
        self.left = other[0]
        self.top = other[1] - self.height / 2

    def as_list(self) -> list[float]:
        return [self.left, self.top, self.width, self.height]

    def __add__(self, other):
        result = Rectangle()
        result.left = min(self.left, other.left)
        result.top = min(self.top, other.top)
        result.width = max(self.right, other.right) - result.left
        result.height = max(self.bottom, other.bottom) - result.top
        return result

    def overlaps(self, other) -> bool:
        return self.left < other.right and other.left < self.right and self.top < other.bottom and other.top < self.bottom

    def __contains__(self, other) -> bool:
        return self.left <= other.left <= self.right and self.left <= other.right <= self.right and self.top <= other.top <= self.bottom and self.top <= other.bottom <= self.bottom

    def area(self) -> float:
        return self.width * self.height

    def __repr__(self):
        return f"Rectangle(left={self.left}, top={self.top}, width={self.width}, height={self.height})"

    def __eq__(self, other):
        return self.as_list() == other.as_list()

    def adjacent_to(self, other):
        return (self.top == other.top) != (self.right == other.right) != (self.bottom == other.bottom) != (
                    self.left == other.left)


