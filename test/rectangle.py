from src.rectangle import Rectangle


def test__add__():
    assert Rectangle(0, 0, 10, 10) + Rectangle(5, 5, 10, 10) == Rectangle(0, 0, 15, 15)
    assert Rectangle(0, 0, 1, 1) + Rectangle(1, 0, 1, 1) == Rectangle(0, 0, 2, 1)

def test_overlaps():
    assert Rectangle(0, 0, 10, 10).overlaps(Rectangle(5, 5, 10, 10))
    assert not Rectangle(0, 0, 10, 10).overlaps(Rectangle(10, 10, 10, 10))

def test__contains__():
    assert Rectangle(25, 25, 25, 25) in Rectangle(0, 0, 100, 100)
    assert Rectangle(0, 0, 10, 10) not in Rectangle(5, 5, 10, 10)
    assert Rectangle(0, 0, 10, 10) in Rectangle(0, 0, 10, 10)

def test_adjacent_to():
    assert Rectangle(0, 0, 10, 10).adjacent_to(Rectangle(10, 0, 10, 10))
    assert not Rectangle(0, 0, 10, 10).adjacent_to(Rectangle(11, 0, 10, 10))
    assert not Rectangle(0, 0, 10, 10).adjacent_to(Rectangle(5, 5, 10, 10))
