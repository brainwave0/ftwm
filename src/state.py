from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from .center_gravity_layout import CenterGravityLayout

if TYPE_CHECKING:
    from configparser import ConfigParser
    from .window import Window
    from .screen import Screen
    import asyncio

    
    from wlroots.wlr_types import (  # type: ignore[attr-defined]
        Seat,
        Scene,
        Cursor,
        XdgShell,
        Keyboard,
        Backend,
        Output,
        Display,
        OutputLayout,
        SceneLayout,
        XCursorManager,
    )
    from wlroots.allocator import Allocator
    from wlroots.renderer import Renderer
    from .layout import Layout
from wlroots.wlr_types import SceneTree  # type: ignore[attr-defined]
import numpy
from .rectangle import Rectangle

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
        display: Display,
        xcursor_manager: XCursorManager
    ):
        self.settings = settings
        self.windows = windows
        self.screen = screen
        self.tasks = tasks
        self.paused = paused
        self.seat = seat
        self._active_window: Optional[Window] = None
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
        self.xcursor_manager = xcursor_manager
        self.window_delta = (0, 0)
        self.window_group_tree = SceneTree.create(scene.tree)

    def new_id(self) -> int:
        self._prev_id += 1
        return self._prev_id

    @property
    def active_window(self) -> Optional[Window]:
        return self._active_window
    
    @active_window.setter
    def active_window(self, window: Window) -> None:
        if self._active_window is not None:
            self._active_window._xdg_surface.set_activated(False)
        window._scene_node.raise_to_top()
        window._xdg_surface.set_activated(True)
        if self.keyboard:
            self.reset_keyboard_focus()
        self._active_window = window

        # move to the top of the stack in case a window is destroyed and a new active window is needed
        self.windows.remove(window)
        self.windows.append(window)

    def reset_keyboard_focus(self) -> None:
        assert self.keyboard is not None
        if self.active_window is not None:
            self.seat.keyboard_clear_focus()
            self.seat.keyboard_notify_enter(
                self.active_window._xdg_surface.surface, self.keyboard
            )

    def reset_active_window(self) -> None:
        self.active_window = self.windows[-1]
        

    def window_at(self, x: float, y: float) -> Optional[Window]:
        return next((i for i in self.windows if Rectangle(x, y, 0, 0) in i.virtual), None)
