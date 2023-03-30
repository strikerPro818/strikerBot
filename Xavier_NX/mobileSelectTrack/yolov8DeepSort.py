import cv2
import numpy as np
from ultralytics import YOLO
import time
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config

model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
frame_count = 0
start_time = time.time()
cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')
use_cuda = True
tracker = build_tracker(cfg, use_cuda)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    results = model.predict(frame, stream=True)

    # Prepare the boxes, scores, and classes for the DeepSORT tracker
    boxes = []
    scores = []
    classes = []
    for result in results:
        boxes.extend(result.boxes.xywh.to("cpu").numpy())
        scores.extend(result.boxes.conf.to("cpu").numpy())
        classes.extend(result.boxes.cls.to("cpu").numpy())

    # Convert lists to NumPy arrays
    boxes = np.array(boxes)
    scores = np.array(scores)
    classes = np.array(classes)

    # Update the tracker with the detected boxes, scores, and classes
    tracked_objects = tracker.update(boxes, scores, classes, frame)

    # Draw tracked objects on the frame
    for x1, y1, x2, y2, cls, track_id in tracked_objects:
        if cls == 0:  # "person" class index is 0
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)
            cv2.putText(frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Calculate fps and display as text overlay
    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = frame_count / elapsed_time
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    frame_count += 1
    if frame_count % 10 == 0:  # Calculate fps every 10 frames
        frame_count = 0
        start_time = time.time()

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
