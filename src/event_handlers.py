from .placement import place
from .window import Window
from .state import State
from .misc import delay_resume_panning, view_at
from pywayland.server import Listener  # type: ignore[attr-defined]
from wlroots.wlr_types.pointer import PointerButtonEvent
from wlroots.wlr_types.keyboard import KeyboardKeyEvent
from wlroots.wlr_types import Scene, InputDevice, Keyboard, OutputState, SceneOutput  # type: ignore[attr-defined]
from wlroots.wlr_types.input_device import ButtonState, InputDeviceType
from pywayland.protocol.wayland import WlKeyboard  # type: ignore[attr-defined]
from wlroots.wlr_types.xdg_shell import XdgSurface
import logging
from wlroots.util.clock import Timespec


def register_events(state: State) -> None:
    logging.info("registering events")
    state.xdg_shell.new_surface_event.add(  # type: ignore[no-untyped-call]
        Listener(lambda listener, xdg_surface: new_xdg_surface(state, xdg_surface))
    )
    state.backend.new_input_event.add(
        Listener(lambda listener, input_device: new_input(state, input_device))
    )
    print("adding output event listener")
    state.backend.new_output_event.add(Listener(lambda listener, output: new_output(state, output)))

def new_xdg_surface(state: State, xdg_surface: XdgSurface) -> None:
    logging.info("new_xdg_surface")
    scene_tree = Scene.xdg_surface_create(state.scene.tree, xdg_surface)
    window = Window(state, xdg_surface, scene_tree.node)
    geometry = xdg_surface.get_geometry()
    window.virtual.size = (geometry.width, geometry.height)
    place(state, state.windows, window)
    state.windows.append(window)
    xdg_surface.destroy_event.add(Listener(lambda listener, data: window.kill()))


def pointer_button(state: State, event: PointerButtonEvent) -> None:
    logging.info("pointer button event")
    if event.button_state == ButtonState.PRESSED:
        state.paused = True
        window = view_at(state, state.cursor.x, state.cursor.y)[0]
        if window:
            window.focus()
    else:
        delay_resume_panning(state)


def key_press(state: State, key_event: KeyboardKeyEvent) -> None:
    logging.info("key press event")
    if key_event.state == WlKeyboard.key_state.pressed:
        state.paused = True
    else:
        delay_resume_panning(state)


def new_input(state: State, input_device: InputDevice) -> None:
    logging.info("new input")
    if input_device.type == InputDeviceType.KEYBOARD:
        state.keyboard = Keyboard.from_input_device(input_device)
        state.keyboard.key_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, key_event: key_press(state, key_event))
        )
    elif input_device.type == InputDeviceType.POINTER:
        state.cursor.attach_input_device(input_device)
        state.cursor.button_event.add(  # type: ignore[no-untyped-call]
            Listener(lambda listener, event: pointer_button(state, event))
        )

def new_output(state, output):
    logging.info("new output")
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
    output.frame_event.add(Listener(lambda listener, data: output_frame(state)))
    output.request_state_event.add(Listener(lambda listener, request: output_request_state(state, request)))
    scene_output = SceneOutput.create(state.scene, output)
    if state.scene_layout:
        state.scene_layout.add_output(l_output, scene_output)

def output_frame(state):
    output = state.outputs[0]
    scene_output = state.scene.get_scene_output(output)
    scene_output.commit()
    now = Timespec.get_monotonic_time()
    scene_output.send_frame_done(now)

def output_request_state(state, request):
    output = state.outputs[0]
    output.commit(request.state)

