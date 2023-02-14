from typing import Iterable

import mediapipe
from xcffib import Connection
from xcffib.xproto import (
    CW,
    EventMask,
)

from .window import Window

face_detection = mediapipe.solutions.face_detection


def pan(
    windows: Iterable[Window], delta: tuple[float, float], scale: float = 1
) -> None:
    """
    Pans windows.

    delta: How far to move each window from their virtual positions.
    scale: Multiplied with delta to affect panning sensitivity.
    """
    for window in windows:
        window.position = (
            int(window.virtual.position[0] + delta[0] * scale),
            int(window.virtual.position[1] + delta[1] * scale),
        )


def register_wm(connection: Connection) -> None:
    root_id = connection.get_setup().roots[0].root
    connection.core.ChangeWindowAttributes(
        root_id,
        CW.EventMask,
        [EventMask.SubstructureRedirect | EventMask.SubstructureNotify],
    )
