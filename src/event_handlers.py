import logging
from .util import view_at
from .window import Window
from .state import State
from .panning import delay_resume_panning
from pywayland.server import Listener  # type: ignore[attr-defined]
from wlroots.wlr_types.pointer import PointerButtonEvent
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
from pywayland.protocol.wayland import WlKeyboard  # type: ignore[attr-defined]
from wlroots.wlr_types.xdg_shell import XdgSurface
import logging
from wlroots.util.clock import Timespec


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


def new_xdg_surface(state: State, xdg_surface: XdgSurface) -> None:
    scene_tree = Scene.xdg_surface_create(state.scene.tree, xdg_surface)
    window = Window(state, xdg_surface, scene_tree.node)
    geometry = xdg_surface.get_geometry()
    window.width = geometry.width or 256
    window.height = geometry.height or 256
    state.layout.place(window)
    state.windows.append(window)
    xdg_surface.destroy_event.add(Listener(lambda listener, data: window.kill()))  # type: ignore[no-untyped-call]
    if state.active_window is None:
        state.active_window = window


def pointer_button(state: State, event: PointerButtonEvent) -> None:
    if event.button_state == ButtonState.PRESSED:
        state.paused = True
        window = view_at(state, state.cursor.x, state.cursor.y)[0]
        if window:
            state.active_window = window
    else:
        delay_resume_panning(state)


def key_press(state: State, key_event: KeyboardKeyEvent) -> None:
    if key_event.state == WlKeyboard.key_state.pressed:
        state.paused = True
    else:
        delay_resume_panning(state)


def new_input(state: State, input_device: InputDevice) -> None:
    if input_device.type == InputDeviceType.KEYBOARD:
        state.keyboard = Keyboard.from_input_device(input_device)
        state.keyboard.key_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, key_event: key_press(state, key_event))
        )
        state.reset_keyboard_focus()
    elif input_device.type == InputDeviceType.POINTER:
        state.cursor.attach_input_device(input_device)
        state.cursor.button_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, event: pointer_button(state, event))
        )


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
        logging.warning("Failed to add output to layout.")
        return
    
    output.frame_event.add(Listener(lambda listener, data: output_frame(state)))  # type: ignore[no-untyped-call]
    output.request_state_event.add(
        Listener(lambda listener, request: output_request_state(state, request))
    )  # type: ignore[no-untyped-call]
    scene_output = SceneOutput.create(state.scene, output)
    if state.scene_layout:
        state.scene_layout.add_output(l_output, scene_output)
    dimensions = state.output_layout.get_box()
    state.screen.geometry.size = (dimensions.width, dimensions.height)


def output_frame(state: State) -> None:
    output = state.outputs[0]
    scene_output = state.scene.get_scene_output(output)
    scene_output.commit()
    now = Timespec.get_monotonic_time()
    scene_output.send_frame_done(now)



def output_request_state(state: State, request) -> None:  # type: ignore[no-untyped-def]
    output = state.outputs[0]
    output.commit(request.state)
