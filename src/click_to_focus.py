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

from src.window import active_window, Window


def register_for_button_press_events(connection: Connection, window_id: int) -> None:
    connection.core.UngrabButton(ButtonIndex.Any, window_id, Grab.Any)

    # GrabButton can register the window for button press events, but it blocks clicks to other windows, so allow_events
    # is used later.
    connection.core.GrabButton(
        1,
        window_id,
        EventMask.ButtonPress,
        GrabMode.Sync,
        GrabMode.Async,
        xcffib.xproto.Window._None,
        Cursor._None,
        ButtonIndex._1,
        ModMask.Any,
    )


def allow_events(connection: xcffib.Connection) -> None:
    """
    Allows clicks to other windows when button press events are grabbed by another window.
    """
    connection.core.AllowEvents(Allow.ReplayPointer, CurrentTime)


def focus_window(
    connection: xcffib.Connection, window_id: int, windows: list[Window]
) -> None:
    """
    Focuses the given window.
    """
    active_window_ = active_window(windows)
    if active_window_ is None or active_window_.id != window_id:
        # there is no active window, or this window has not been focused yet

        connection.core.SetInputFocus(InputFocus.PointerRoot, window_id, CurrentTime)
        for window in windows:
            if window.id == window_id:
                window.active = True
            else:
                window.active = False
