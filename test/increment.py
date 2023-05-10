def test_increment():
    assert increment("foo", 1, 1) == 1.2
    assert increment("foo", 1.2, 1) == 1.45
    assert increment("foo", 1.45, 1) == 1.95
    assert increment("foo", 1.95, -1) == 1.7
    assert increment("foo", 1.7, -1) == 1.575
