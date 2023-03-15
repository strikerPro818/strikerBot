import cv2
import torch
import numpy as np
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')

# Set use_cuda flag to True if you have a GPU
use_cuda = True

# Instantiate detector and tracker
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False).cuda()
tracker = build_tracker(cfg, use_cuda)

# Open webcam capture
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect objects using YOLOv5
    results = model(frame, size=640)

    # Get the coordinates of the detected objects
    bboxes = results.xywh[0][:, :4].cpu().numpy()
    confidences = results.xywh[0][:, 4].cpu().numpy()
    classes = results.xywh[0][:, 5].cpu().numpy()

    # Filter out non-person objects
    person_idxs = np.where(classes == 0)[0]
    bboxes = bboxes[person_idxs]
    confidences = confidences[person_idxs]

    # Update tracker with person bounding boxes and confidences
    outputs = tracker.update(bboxes, confidences, np.zeros_like(person_idxs), frame)

    # Draw bounding boxes and track IDs on the frame for people only
    for output in outputs:
        x1, y1, x2, y2, track_id = map(int, output[:5])
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, str(track_id), (x1, y1-10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
