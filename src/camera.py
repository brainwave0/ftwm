from typing import Optional
import cv2
from threading import Thread
from numpy.typing import ArrayLike


class Camera:
    def __init__(
        self, index: int, frame_size: Optional[tuple[int, int]] = None, fps: float = 60
    ) -> None:
        self._video_capture = cv2.VideoCapture(index)
        self._frame: Optional[ArrayLike] = None
        self._video_capture.set(cv2.CAP_PROP_FPS, fps)
        if frame_size is not None:
            self._video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, frame_size[0])
            self._video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_size[1])
        Thread(target=self._set_frames, daemon=True).start()

    def get_frame(self) -> Optional[ArrayLike]:
        return self._frame

    def _set_frames(self) -> None:
        while True:
            success, frame = self._video_capture.read()
            if not success:
                raise RuntimeError("Failed to get frame from camera.")
            self._frame = frame
