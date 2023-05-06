import xcffib  # type: ignore[import]
from xcffib import Connection
from xcffib.xproto import (  # type: ignore[import]
    MapRequestEvent,
    DestroyNotifyEvent,
    ButtonPressEvent,
    WindowError,
    DrawableError,
)

from .placement import place
from .screen import Screen
from .window import Window
from .click_to_focus import register_for_button_press_events, allow_events, focus_window
from .state import State
import logging
from reactivex.abc import ObserverBase, SchedulerBase, DisposableBase
import asyncio
from typing import Callable, Any, Optional
from reactivex.typing import Subscription


def map_request(state: State, event: MapRequestEvent) -> None:
    assert not state.connection.invalid()
    window = Window(state, event.window)
    geometry = state.connection.core.GetGeometry(window.id).reply()
    window.virtual.size = (geometry.width, geometry.height)
    place(state, state.windows, window)
    state.windows.append(window)
    state.connection.core.MapWindow(event.window)
    register_for_button_press_events(state, event.window)


def destroy_notify(state: State, event: DestroyNotifyEvent) -> None:
    try:
        window = next(i for i in state.windows if i.id == event.window)
        state.windows.remove(window)
    except StopIteration:
        pass


def button_press(state: State, event: ButtonPressEvent) -> None:
    if any(event.event == window.id for window in state.windows):
        focus_window(state, event.event)
    allow_events(state)


def handle_event(state: State, event: xcffib.Event) -> None:
    if isinstance(event, MapRequestEvent):
        map_request(state, event)
    elif isinstance(event, DestroyNotifyEvent):
        destroy_notify(state, event)
    elif isinstance(event, ButtonPressEvent):
        button_press(state, event)
    else:
        pass


def push_x_events(state, frequency):  # type: ignore[no-untyped-def]

    def push_x_events_(observer, scheduler):  # type: ignore[no-untyped-def]

        async def push_x_events__(observer, scheduler):  # type: ignore[no-untyped-def]
            while True:
                try:
                    event = state.connection.poll_for_event()
                    if event is not None:
                        observer.on_next(event)
                    else:
                        state.connection.flush()
                        await asyncio.sleep(1 / frequency)
                except WindowError:
                    pass
                except DrawableError:
                    pass
                except xcffib.Error as e:
                    raise e

        state.tasks.add(asyncio.create_task(push_x_events__(observer, scheduler)))

    return push_x_events_
