def test_focus_window():
    state = State.__new__(State)
    state.connection = Mock()

    state.windows = [Window.__new__(Window)] * 2
    windows[0].active = True
    windows[1].active = False
    windows[0].id = 0
    windows[0].id = 1
    focus_window(state, 0)
    assert windows[0].active == True
    assert windows[1].active == False
     
    state.windows = [Window.__new__(Window)] * 2
    windows[0].active = False
    windows[1].active = True
    windows[0].id = 0
    windows[0].id = 1
    focus_window(state, 0)
    assert windows[0].active == True
    assert windows[1].active == False

    state.windows = [Window.__new__(Window)] * 2
    windows[0].active = False
    windows[1].active = False
    windows[0].id = 0
    windows[0].id = 1
    focus_window(state, 0)
    assert windows[0].active == True
    assert windows[1].active == False

    state.windows = [Window.__new__(Window)] * 2
    windows[0].active = True
    windows[1].active = True
    windows[0].id = 0
    windows[0].id = 1
    focus_window(state, 0)
    assert windows[0].active == True
    assert windows[1].active == False
