from .util import view_at
from .window import Window
from .state import State
from .panning import delay_resume_panning
from pywayland.server import Listener  # type: ignore[attr-defined]
from wlroots.wlr_types.pointer import (
    PointerButtonEvent,
    PointerMotionEvent,
    PointerMotionAbsoluteEvent,
)
from wlroots.wlr_types.keyboard import KeyboardKeyEvent


from wlroots.wlr_types import (  # type: ignore[attr-defined]
    Scene,
    InputDevice,
    Keyboard,
    OutputState,
    SceneOutput,
    Output,
)
from wlroots.wlr_types.input_device import ButtonState, InputDeviceType
from pywayland.protocol.wayland import WlKeyboard, WlSeat  # type: ignore[attr-defined]
from wlroots.wlr_types.xdg_shell import XdgSurface, XdgSurfaceRole
from wlroots.util.clock import Timespec
from wlroots.wlr_types.cursor import WarpMode
from wlroots.wlr_types import XCursorManager, SceneTree  # type: ignore[attr-defined]
from .rectangle import Rectangle
import numpy
from xkbcommon import xkb  # type: ignore[import-untyped]
from weakref import WeakKeyDictionary
from typing import cast, Any

_weakkeydict: WeakKeyDictionary[Any, Any] = WeakKeyDictionary()


def register_events(state: State) -> None:
    state.xdg_shell.new_surface_event.add(  # type: ignore[no-untyped-call]
        Listener(lambda listener, xdg_surface: new_xdg_surface(state, xdg_surface))
    )
    state.backend.new_input_event.add(
        Listener(lambda listener, input_device: new_input(state, input_device))
    )
    state.backend.new_output_event.add(
        Listener(lambda listener, output: new_output(state, output))
    )
    state.seat.request_set_cursor_event.add(Listener(lambda listener, event: set_cursor(state, event)))  # type: ignore[no-untyped-call]
    state.cursor.motion_event.add(Listener(lambda listener, event: cursor_motion(state, event)))  # type: ignore[no-untyped-call]
    state.cursor.motion_absolute_event.add(Listener(lambda listener, event: cursor_motion_absolute(state, event)))  # type: ignore[no-untyped-call]
    state.cursor.axis_event.add(Listener(lambda listener, event: cursor_axis(state, event)))  # type: ignore[no-untyped-call]
    state.cursor.frame_event.add(Listener(lambda listener, event: cursor_frame(state)))  # type: ignore[no-untyped-call]


def new_xdg_surface(state: State, xdg_surface: XdgSurface) -> None:
    if xdg_surface.role == XdgSurfaceRole.POPUP:
        if parent_xdg_surface := XdgSurface.try_from_surface(xdg_surface.popup.parent):
            parent_scene_tree = cast(SceneTree, parent_xdg_surface.data)
            scene_tree = Scene.xdg_surface_create(parent_scene_tree, xdg_surface)
            xdg_surface.data = scene_tree
        return
    assert xdg_surface.role == XdgSurfaceRole.TOPLEVEL
    scene_tree = Scene.xdg_surface_create(state.window_group_tree, xdg_surface)
    window = Window(state, xdg_surface, scene_tree.node)
    geometry = xdg_surface.get_geometry()
    window.set_width(geometry.width or 256)
    window.set_height(geometry.height or 256)
    state.layout.place(window)
    state.windows.append(window)
    xdg_surface.destroy_event.add(Listener(lambda listener, data: state.remove(window)))  # type: ignore[no-untyped-call]
    if state.get_active_window() is None:
        state.set_active_window(window)

    # Keep the node alive for as long as the Window, so that the Window is accessible at its data struct member.
    scene_node = scene_tree.node
    scene_node.data = window
    _weakkeydict[window] = scene_node

    xdg_surface.data = scene_tree


def pointer_button(state: State, event: PointerButtonEvent) -> None:
    state.seat.pointer_notify_button(event.time_msec, event.button, event.button_state)
    if event.button_state == ButtonState.PRESSED:
        state.paused = True
        relative_coordinates = tuple(
            numpy.array([state.cursor.x, state.cursor.y])
            - numpy.array(
                [state.window_group_tree.node.x, state.window_group_tree.node.y]
            )
        )
        window = state.window_at(*relative_coordinates)
        if window:
            state.set_active_window(window)
    else:
        delay_resume_panning(state)


def key_press(state: State, key_event: KeyboardKeyEvent) -> None:
    if key_event.state == WlKeyboard.key_state.pressed:
        state.paused = True
    else:
        delay_resume_panning(state)
    state.seat.keyboard_notify_key(key_event)


def new_input(state: State, input_device: InputDevice) -> None:
    if input_device.type == InputDeviceType.KEYBOARD:
        state.keyboard = Keyboard.from_input_device(input_device)
        xkb_context = xkb.Context()
        keymap = xkb_context.keymap_new_from_names()
        state.keyboard.set_keymap(keymap)
        state.keyboard.set_repeat_info(25, 600)
        state.seat.set_keyboard(state.keyboard)
        state.keyboard.key_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, key_event: key_press(state, key_event))
        )
        state.keyboard.modifiers_event.add(Listener(lambda listener, data: keyboard_modifiers(state)))  # type: ignore[no-untyped-call]
        state.reset_keyboard_focus()
    elif input_device.type == InputDeviceType.POINTER:
        state.cursor.attach_input_device(input_device)
        state.cursor.button_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, event: pointer_button(state, event))
        )
    capabilities = 0
    if state.cursor is not None:
        capabilities |= WlSeat.capability.pointer
    if state.keyboard is not None:
        capabilities |= WlSeat.capability.keyboard
    state.seat.set_capabilities(capabilities)


def new_output(state: State, output: Output) -> None:
    output.init_render(state.allocator, state.renderer)
    output_state = OutputState()
    output_state.set_enabled(True)
    if mode := output.preferred_mode():
        output_state.set_mode(mode)
    output.commit(output_state)
    output_state.finish()
    state.outputs.append(output)
    l_output = state.output_layout.add_auto(output)
    if not l_output:
        return

    output.frame_event.add(Listener(lambda listener, data: output_frame(state)))  # type: ignore[no-untyped-call]
    output.request_state_event.add(
        Listener(lambda listener, request: output_request_state(state, request))
    )  # type: ignore[no-untyped-call]
    scene_output = SceneOutput.create(state.scene, output)
    if state.scene_layout:
        state.scene_layout.add_output(l_output, scene_output)
    dimensions = state.output_layout.get_box()
    state.screen.geometry.set_size((dimensions.width, dimensions.height))


def output_frame(state: State) -> None:
    output = state.outputs[0]
    scene_output = state.scene.get_scene_output(output)
    scene_output.commit()
    now = Timespec.get_monotonic_time()
    scene_output.send_frame_done(now)


def output_request_state(state: State, request) -> None:  # type: ignore[no-untyped-def]
    output = state.outputs[0]
    output.commit(request.state)


def set_cursor(state: State, event) -> None:  # type: ignore[no-untyped-def]
    state.cursor.set_surface(event.surface, event.hotspot)


def process_cursor_motion(state: State, time) -> None:  # type: ignore[no-untyped-def]
    state.paused = True
    delay_resume_panning(state)
    view, surface, sx, sy = view_at(state, state.cursor.x, state.cursor.y)
    if view is None:
        state.cursor.set_xcursor(state.xcursor_manager, "default")
    if surface is None:
        # Clear pointer focus so future button events and such are not sent
        # to the last client to have the cursor over it.
        state.seat.pointer_clear_focus()
    else:
        # Send pointer enter and motion events.
        state.seat.pointer_notify_enter(surface, sx, sy)
        state.seat.pointer_notify_motion(time, sx, sy)


def cursor_motion_absolute(state: State, event: PointerMotionAbsoluteEvent) -> None:
    state.cursor.warp(
        WarpMode.AbsoluteClosest,
        event.x,
        event.y,
        input_device=event.pointer.base,
    )
    process_cursor_motion(state, event.time_msec)


def cursor_axis(state: State, event) -> None:  # type: ignore[no-untyped-def]
    state.seat.pointer_notify_axis(
        event.time_msec,
        event.orientation,
        event.delta,
        event.delta_discrete,
        event.source,
    )


def cursor_frame(state: State) -> None:
    state.seat.pointer_notify_frame()


def cursor_motion(state: State, event: PointerMotionEvent) -> None:
    state.cursor.move(
        event.delta_x,
        event.delta_y,
        input_device=event.pointer.base,
    )
    process_cursor_motion(state, event.time_msec)


def keyboard_modifiers(state: State) -> None:
    if state.keyboard is not None:
        state.seat.keyboard_notify_modifiers(state.keyboard.modifiers)
