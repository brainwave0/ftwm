from functools import reduce

import cv2
import mediapipe as mp

mp_face_detection = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

# For static images:
IMAGE_FILES = []
with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0) as face_detection:
    for idx, file in enumerate(IMAGE_FILES):
        image = cv2.imread(file)
        # Convert the BGR image to RGB and process it with MediaPipe Face Detection.
        results = face_detection.process(
            cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        # Draw face detections of each face.
        if not results.detections:
            continue
        annotated_image = image.copy()
        for detection in results.detections:
            print('Nose tip:')
            print(mp_face_detection.get_key_point(
                detection, mp_face_detection.FaceKeyPoint.NOSE_TIP))
            mp_drawing.draw_detection(annotated_image, detection)
        cv2.imwrite('/tmp/annotated_image' +
                    str(idx) + '.png', annotated_image)

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_face_detection.FaceDetection(
        model_selection=0, min_detection_confidence=0) as face_detection:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = face_detection.process(image)

        # Draw the face detection annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.detections:
            detection = results.detections[0]
            points = [mp_face_detection.get_key_point(detection, i) for i in mp_face_detection.FaceKeyPoint]
            points = [(point.x * image.shape[1], point.y * image.shape[0]) for point in points]
            box = detection.location_data.relative_bounding_box
            box_center = (box.xmin * image.shape[1] + box.width / 2, box.ymin * image.shape[0] + box.height / 2)
            points.append(box_center)
            point = reduce(lambda a, b: (a[0] + b[0], a[1] + b[1]), points)
            point = (int(point[0] / len(points)), int(point[1] / len(points)))
            # for detection in results.detections:
            cv2.drawMarker(image, point, (255, 0, 0))
            # cv2.drawMarker(image, (detection.relative_bounding_box), (255, 0, 0))
        # Flip the image horizontally for a selfie-view display.
        cv2.imshow('MediaPipe Face Detection', cv2.flip(image, 1))
        if cv2.waitKey(int(1000 / 30 * 2)) & 0xFF == 27:
            break
cap.release()
