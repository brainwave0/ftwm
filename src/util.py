from glob import glob
import shutil
from .camera import Camera
from os import makedirs
from pathlib import Path
from configparser import ConfigParser
from wlroots.wlr_types import Surface, SceneNodeType, SceneBuffer, SceneSurface, SceneTree  # type: ignore[attr-defined]
from typing import cast, Optional
from .state import State
from .window import Window
from xdg_base_dirs import xdg_config_home
import cv2
def view_at(
    state: State, layout_x: float, layout_y: float
) -> tuple[Window | None, Surface | None, float, float]:
    maybe_node = state.scene.tree.node.node_at(
        layout_x,
        layout_y,
    )
    if maybe_node is None or maybe_node[0].type != SceneNodeType.BUFFER:
        return None, None, 0, 0

    node, sx, sy = maybe_node
    scene_buffer = SceneBuffer.from_node(node)
    if scene_buffer is None:
        return None, None, 0, 0
    scene_surface = SceneSurface.from_buffer(scene_buffer)
    if scene_surface is None:
        return None, None, 0, 0

    surface = scene_surface.surface
    tree = cast(SceneTree, node.parent)

    # Find the node corresponding to the view at the root of this tree
    while tree.node.data is not None:
        tree = cast(SceneTree, tree.node.parent)

    return tree.node.data, surface, sx, sy
def get_settings() -> ConfigParser:
    source_directory = Path(__file__).resolve().parent
    settings_file_path = xdg_config_home() / "ftwm/settings.ini"
    defaults = source_directory.parent / "settings.ini"
    if not settings_file_path.is_file():
        makedirs(settings_file_path.parent, exist_ok=True)
        shutil.copy(defaults, settings_file_path)
    settings = ConfigParser()
    settings.read([defaults, settings_file_path])
    return settings
def get_and_set_up_camera(
    state: State, face_detector: cv2.FaceDetectorYN
) -> Camera:
    fps = state.settings.getint("Camera", "fps")
    if (
        "capture_width" in state.settings["Camera"]
        and "capture_height" in state.settings["Camera"]
    ):
        size = (
            state.settings.getint("Camera", "capture_width"),
            state.settings.getint("Camera", "capture_height"),
        )
    else:
        size = None
    if "index" in state.settings["Camera"]:
        camera = Camera(state.settings.getint("Camera", "index"), size, fps)
    else:
        index = auto_camera_index()
        if index is not None:
            camera = Camera(index, size, fps)
        else:
            raise RuntimeError("Could not find a camera.")
    return camera
def auto_camera_index() -> Optional[int]:
    video_capture = None
    index = None
    for index in sorted(
        int(device.replace("/dev/video", "")) for device in glob("/dev/video*")
    ):
        video_capture = cv2.VideoCapture(index)
        _, frame = video_capture.read()
        if frame is not None:
            break
    if video_capture is not None:
        video_capture.release()
    return index
