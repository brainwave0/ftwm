from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from .center_gravity_layout import CenterGravityLayout

if TYPE_CHECKING:
    from configparser import ConfigParser
    from .window import Window
    from .screen import Screen
    import asyncio
    from wlroots.wlr_types import Seat, Scene, Cursor, XdgShell, Keyboard, Backend, Output, Display, OutputLayout, SceneLayout  # type: ignore[attr-defined]
    from wlroots.allocator import Allocator
    from wlroots.renderer import Renderer
    from .layout import Layout


class State:
    def __init__(
        self,
        settings: ConfigParser,
        windows: list[Window],
        screen: Screen,
        tasks: dict[str, asyncio.Task[None]],
        paused: bool,
        seat: Seat,
        scene: Scene,
        cursor: Cursor,
        xdg_shell: XdgShell,
        backend: Backend,
        scene_layout: SceneLayout,
        allocator: Allocator,
        renderer: Renderer,
        output_layout: OutputLayout,
        display: Display
    ):
        self.settings = settings
        self.windows = windows
        self.screen = screen
        self.tasks = tasks
        self.paused = paused
        self.seat = seat
        self.active_window: Optional[Window] = None
        self.scene = scene
        self.cursor = cursor
        self.xdg_shell = xdg_shell
        self._prev_id = 0
        self.keyboard: Optional[Keyboard] = None
        self.backend = backend
        self.scene_layout = scene_layout
        self.allocator = allocator
        self.renderer = renderer
        self.outputs: list[Output] = []
        self.output_layout = output_layout
        self.display = display
        self.layout = CenterGravityLayout(self)

    def new_id(self) -> int:
        self._prev_id += 1
        return self._prev_id
