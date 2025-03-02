from src.face_tracking import FaceTracker
import cv2
from src.camera import Camera
from src.util import auto_camera_index
face_tracker = FaceTracker((640, 480), 4, 60, 0.5, "./assets/face_detection_yunet_2023mar.onnx", 96)
camera = Camera(auto_camera_index(), (640, 480), 60)
while True:
    frame = camera.get_frame()
    if frame is not None:
        point = face_tracker.get_point(frame)
        if point is not None:
            if face_tracker.tracking_succeeded:
                color = (0, 255, 0)
            else:
                color = (0, 0, 255)
            x, y = point
            cv2.circle(frame, (int(x), int(y)), radius=4, color=color, thickness=-1)
            top_left, bottom_right = face_tracker._bounding_box_points(point)
            cv2.rectangle(frame, tuple(map(int, top_left)), tuple(map(int, bottom_right)), color)
            cv2.imshow("frame", frame)
        cv2.waitKey(1)
