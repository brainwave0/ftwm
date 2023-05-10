from src.state import State
from src.window import Window
from src.click_to_focus import focus_window
from unittest.mock import Mock


def test_focus_window():
    state = State.__new__(State)
    state.connection = Mock()

    state.windows = [Window.__new__(Window) for i in range(2)]
    state.windows[0].active = True
    state.windows[1].active = False
    state.windows[0].id = 0
    state.windows[1].id = 1
    focus_window(state, 0)
    assert state.windows[0].active == True
    assert state.windows[1].active == False
     
    state.windows[0].active = False
    state.windows[1].active = True
    state.windows[0].id = 0
    state.windows[1].id = 1
    focus_window(state, 0)
    assert state.windows[0].active == True
    assert state.windows[1].active == False

    state.windows[0].active = False
    state.windows[1].active = False
    state.windows[0].id = 0
    state.windows[1].id = 1
    focus_window(state, 0)
    assert state.windows[0].active == True
    assert state.windows[1].active == False

    state.windows[0].active = True
    state.windows[1].active = True
    state.windows[0].id = 0
    state.windows[1].id = 1
    focus_window(state, 0)
    assert state.windows[0].active == True
    assert state.windows[1].active == True  # nothing is done because the given window is already focused
