import xcffib  # type: ignore[import]
from xcffib import CurrentTime, Connection
from xcffib.xproto import (  # type: ignore[import]
    ButtonIndex,
    EventMask,
    Grab,
    GrabMode,
    Cursor,
    ModMask,
    Allow,
    InputFocus,
)
from .state import State
from src.window import get_active_window, Window


# 0111
def register_for_button_press_events(state: State, window_id: int) -> None:
    # state.connection.core.UngrabButton(ButtonIndex.Any, window_id, ModMask.Any)

    # GrabButton can register the window for button press events, but it blocks clicks to other windows, so allow_events
    # is used later.
    state.connection.core.GrabButton(
        1,
        window_id,
        EventMask.ButtonPress,
        GrabMode.Sync,
        GrabMode.Async,
        xcffib.xproto.Window._None,
        Cursor._None,
        ButtonIndex.Any,
        ModMask.Any,
    )

def register_for_key_press_events(state: State, window_id: int) -> None:
    state.connection.core.UngrabKey(Grab.Any, window_id, ModMask.Any)

    # GrabButton can register the window for button press events, but it blocks clicks to other windows, so allow_events
    # is used later.
    state.connection.core.GrabKey(
        1,
        window_id,
        ModMask.Any,
        Grab.Any,
        GrabMode.Async,
        GrabMode.Sync,
    )

def allow_events(state: State) -> None:
    """
    Allows clicks to other windows when button press events are grabbed by another window.
    """
    state.connection.core.AllowEvents(Allow.ReplayPointer, CurrentTime)
    state.connection.core.AllowEvents(Allow.ReplayKeyboard, CurrentTime)


def focus_window(state: State, event_window_id: int) -> None:
    """
    Focuses the given window.
    """
    active_window = get_active_window(state)
    if active_window is None or active_window.id != event_window_id:
        # there is no active window, or this window has not been focused yet

        state.connection.core.SetInputFocus(
            InputFocus.PointerRoot, event_window_id, CurrentTime
        )
        for window in state.windows:
            if window.id == event_window_id:
                window.active = True
            else:
                window.active = False
