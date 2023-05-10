def test_split():
    grid = DynamicGrid()
    assert list(grid) == []

    grid.split(0, 0)
    grid.split(0, 1)
    grid.split(100, 0)
    grid.split(100, 1)
    """
        0  100
      0 +--+
        |  |
    100 +--+
    """
    assert list(grid) == [(Rectangle(0, 0, 100, 100), None)]

    grid.split(50, 0)
    """
        0   50  100
      0 +---+---+
        |   |   |
        |   |   |
        |   |   |
    100 +---+---+
    """
    assert list(grid) == [(Rectangle(0, 0, 50, 100), None), (Rectangle(50, 0, 50, 100), None)]

    grid.split(200, 1)
    """
        0   50  100
      0 +---+---+
        |   |   |
        |   |   |
        |   |   |
    100 +---+---+
        |   |   |
        |   |   |
        |   |   |
    200 +---+---+
    """
    assert list(grid) == [(Rectangle(0, 0, 50, 100), None), (Rectangle(50, 0, 50, 100), None), (Rectangle(0, 100, 50, 100), None), (Rectangle(50, 100, 50, 100), None)]

    grid.split(25, 0)
    """
        0 25 50  100
      0 +-+-+---+
        | | |   |
        | | |   |
        | | |   |
    100 +-+-+---+
        | | |   |
        | | |   |
        | | |   |
    200 +-+-+---+
    """
    assert list(grid) == [
        (Rectangle(0,   0,   25, 100), None), (Rectangle(25,   0,   25, 100), None),     (Rectangle(50, 0,   50, 100), None),
        (Rectangle(0, 100, 25, 100), None), (Rectangle(25, 100, 25, 100), None), (Rectangle(   50, 100, 50, 100), None)
    ]

def test_set_range():
    grid = DynamicGrid()
    grid.set_range(Rectangle(-10, -10, 20, 20), "foo")
    assert list(grid) == [(Rectangle(-10, -10, 20, 20), "foo")]

    grid.set_range(Rectangle(-5, -5, 5, 5), "bar")
    """
       -10 -5  0          10
    -10 +---+---+-----------+
        |foo|foo|   foo     |
    -5  +---+---+-----------|
        |foo|bar|   foo     |
     0  +---+---+-----------|
        |   |   |           |
        |foo|foo|   foo     |
        |   |   |           |
        |   |   |           |
    10  +---+---+-----------+
    """
    assert list(grid) == [(Rectangle(-10, -10, 5, 5), "foo"), (Rectangle(-5, -10, 5, 5), "foo"), (Rectangle(0, -10, 10, 5), "foo"), (Rectangle(-10, -5, 5, 5), "foo"), (Rectangle(-5, -5, 5, 5), "bar"), (Rectangle(0, -5, 10, 5), "foo"), (Rectangle(-10, 0, 5, 10), "foo"), (Rectangle(-5, 0, 5, 10), "foo"), (Rectangle(0, 0, 10, 10), "foo")]

    grid.set_range(Rectangle(-10, -10, 20, 20), None)
    assert list(grid) == [(Rectangle(-10, -10, 5, 5), None), (Rectangle(-5, -10, 5, 5), None), (Rectangle(0, -10, 10, 5), None), (Rectangle(-10, -5, 5, 5), None), (Rectangle(-5, -5, 5, 5), None), (Rectangle(0, -5, 10, 5), None), (Rectangle(-10, 0, 5, 10), None), (Rectangle(-5, 0, 5, 10), None), (Rectangle(0, 0, 10, 10), None)]

def test_get_range():
    grid = DynamicGrid()
    grid.set_range(Rectangle(0, 0, 10, 10), None)
    grid.set_range(Rectangle(0, 0, 5, 5), "a")
    assert list(grid) == [(Rectangle(0, 0, 5, 5), "a"), (Rectangle(5, 0, 5, 5), None), (Rectangle(0, 5, 5, 5), None), (Rectangle(5, 5, 5, 5), None)]

def test_expand():
    grid = DynamicGrid()
    grid.set_range(Rectangle(0, 0, 1, 1), None)
    grid.expand(0, 2, 2, 0)
    assert list(grid) == [(Rectangle(0, 0, 1, 1), None), (Rectangle(1, 0, 1, 1), None), (Rectangle(0, 1, 1, 1), None), (Rectangle(1, 1, 1, 1), None)]

    grid.expand(0, 1, 1, 0)
    assert list(grid) == [(Rectangle(0, 0, 1, 1), None), (Rectangle(1, 0, 1, 1), None), (Rectangle(0, 1, 1, 1), None), (Rectangle(1, 1, 1, 1), None)]
