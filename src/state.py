from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Any

if TYPE_CHECKING:
    from configparser import ConfigParser
    from xcffib import Connection
    from .window import Window
    from .screen import Screen
    import asyncio


class State:
    def __init__(
        self,
        settings: ConfigParser,
        connection: Connection,
        windows: list[Window],
        screen: Screen,
        tasks: dict[str, asyncio.Task[None]],
        paused: bool
    ):
        self.settings = settings
        self.connection = connection
        self.windows = windows
        self.screen = screen
        self.tasks = tasks
        self.paused = paused
