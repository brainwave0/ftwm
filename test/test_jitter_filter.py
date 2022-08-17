from ftwm.jitter_filter import JitterFilter
from collections import deque


def test_jitter_filter():
    filter = JitterFilter((0, 0), 32, 6)
    assert filter.filter((32, 32)) == (0, 0)
    assert filter.filter((33, 33)) == (33, 33)

    prev = (-50, 0)
    filter = JitterFilter(prev, 32, 6)
    rands = [(8, -1), (-2, 3), (6, -8), (-6, 6), (-4, 5), (4, 7)]
    for x, y in rands:
        current = (prev[0] + x, prev[1] + y)
        filter.filter(current)
        prev = current
    assert filter.filter((-50, 0)) == (-50, 0)

    filter = JitterFilter((0, 0), 4, 6)
    filter._prevs = deque([(0, 32), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)])
    for i in range(33, 512):
        assert filter.filter((0, i)) == (0, i)

    filter = JitterFilter((0, 0), 32, 6)
    for i in range(6):
        assert filter.filter((0, 0)) == (0, 0)
    assert filter.filter((64, 32)) == (64, 32)
