from pytest import raises
from ftwm.dynamic_grid import DynamicGrid


def test_split():
    grid = DynamicGrid()
    assert list(grid) == [((0, 0), None)]

    grid.split(10, 0)
    assert list(grid) == [((0, 0), None), ((10, 0), None)]

    grid.split(10, 1)
    assert list(grid) == [((0,  0), None), ((10,  0), None),
                          ((0, 10), None), ((10, 10), None) ]

    grid.split(-10, 0)
    assert list(grid) == [((-10, 0 ), None), ((0,  0), None), ((10,  0), None),
                          ((-10, 10), None), ((0, 10), None), ((10, 10), None) ]

def test_set_range():
    grid = DynamicGrid()
    grid.split(10, 0)
    grid.split(10, 1)

    grid.set_range([0, 0, 10, 10], "foo")
    assert list(grid) == [((0,  0), "foo"), ((10,  0), None),
                          ((0, 10), None ), ((10, 10), None) ]

    grid.set_range([5, 0, 5, 10], "bar")
    assert list(grid) == [((0,  0), "foo"), ((5,  0), "bar"), ((10,  0), None),
                          ((0, 10), None ), ((5, 10), None ), ((10, 10), None) ]

    grid.set_range([0, 5, 10, 5], "baz")
    assert list(grid) == [((0,  0), "foo"), ((5,  0), "bar"), ((10,  0), None),
                          ((0,  5), "baz"), ((5,  5), "baz"), ((10,  5), None),
                          ((0, 10), None ), ((5, 10), None ), ((10, 10), None) ]

    grid.set_range([5, 5, 5, 5], "qux")
    assert list(grid) == [((0,  0), "foo"), ((5,  0), "bar"), ((10,  0), None),
                          ((0,  5), "baz"), ((5,  5), "qux"), ((10,  5), None),
                          ((0, 10), None ), ((5, 10), None ), ((10, 10), None) ]

    grid = DynamicGrid()
    grid.split(100, 0)
    grid.split(100, 1)
    grid.set_range([33, 33, 33, 33], 0)
    assert list(grid) == [((0,   0), None), ((33,   0), None), ((66,   0), None), ((100,   0), None),
                          ((0,  33), None), ((33,  33), 0   ), ((66,  33), None), ((100,  33), None),
                          ((0,  66), None), ((33,  66), None), ((66,  66), None), ((100,  66), None),
                          ((0, 100), None), ((33, 100), None), ((66, 100), None), ((100, 100), None) ]
