from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from configparser import ConfigParser
    from xcffib import Connection
    from .window import Window
    from .screen import Screen


class State:
    def __init__(
        self,
        settings: ConfigParser,
        connection: Connection,
        windows: list[Window],
        screen: Screen,
    ):
        self.settings = settings
        self.connection = connection
        self.windows = windows
        self.screen = screen
