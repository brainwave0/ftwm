from typing import Hashable, Dict

from src import hooks


class IncrementState:
    def __init__(self):
        self.count = 0
        self.prev_dir = None
        self.delta = None


states: Dict[Hashable, IncrementState] = {}


def increment(key: Hashable, number: float, direction: int) -> float:
    assert direction in (-1, 1)
    state = states.get(key, IncrementState())
    # keep track of how many times it has been incremented in the same direction
    if state.prev_dir == direction:
        state.count += 1
    else:
        state.count = 0

    if state.delta is None:
        # initialize delta to 1 / 5 of original value
        state.delta = number / 5
    else:
        # halve the delta if count is zero, multiply it by 1.25 if count is one, and double it if count >= 2
        state.delta *= 0.5 + min(2, state.count) * 0.75
    state.prev_dir = direction
    return number + state.delta * direction
