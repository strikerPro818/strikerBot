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
trackID = 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect objects using YOLOv5
    results = model(frame, size=640)

    # Get the coordinates of the detected objects
    bboxes = results.xywh[0][:, :4].cpu().numpy()
    confidences = results.xywh[0][:, 4].cpu().numpy()
    classes = results.xywh[0][:, 5].cpu().numpy()
    print(classes)

    # Filter out non-chair objects
    chair_idxs = np.where(classes == 56)[0]
    bboxes = bboxes[chair_idxs]
    confidences = confidences[chair_idxs]

    # Update tracker with chair bounding boxes and confidences
    outputs = tracker.update(bboxes, confidences, np.zeros_like(chair_idxs), frame)

    # Draw bounding boxes and track IDs on the frame for chairs only
    for output in outputs:
        x1, y1, x2, y2, _ = map(int, output[:5])
        track_id = int(output[5])
        if track_id == -1:
            track_id = trackID
            trackID += 1
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(frame, str(track_id), (x1, y1 - 10), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 255, 0), 2)

        # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()


nc: 80
names: [
  'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus', 'train', 'truck', 'boat', 'traffic light',
  'fire hydrant', 'stop sign', 'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
  'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag', 'tie', 'suitcase', 'frisbee',
  'skis', 'snowboard', 'sports ball', 'kite', 'baseball bat', 'baseball glove', 'skateboard', 'surfboard',
  'tennis racket', 'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana', 'apple',
  'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza', 'donut', 'cake', 'chair', 'couch',
  'potted plant', 'bed', 'dining table', 'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard',
  'cell phone', 'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock', 'vase',
  'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]
