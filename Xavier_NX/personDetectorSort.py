import cv2
import torch
import numpy as np
import torchvision
from deep_sort import DeepSort
from utils.general import non_max_suppression, scale_coords, xyxy2xywh, plot_one_box

# Load YOLOv5 model
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/', model='yolov5s', source='local')
model.cuda()

# Load DeepSORT model
deepsort = DeepSort('deep_sort_model.pth')

# Set up video capture
cap = cv2.VideoCapture('video.mp4')

# Define confidence threshold and non-maximum suppression threshold for object detection
conf_thresh = 0.5
nms_thresh = 0.5

# Loop through video frames
while True:
    # Read frame from video stream
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to tensor and normalize
    tensor = torchvision.transforms.functional.to_tensor(frame).cuda()
    tensor = tensor.unsqueeze(0) # add batch dimension
    tensor = tensor.float() / 255.0 # normalize

    # Perform object detection with YOLOv5
    with torch.no_grad():
        results = model(tensor)

    # Post-process results
    results = non_max_suppression(results, conf_thresh, nms_thresh)[0]

    # Extract bounding box coordinates and confidence scores for people
    bboxes = []
    scores = []
    for result in results:
        if result[-1] == 0:
            bbox = result[:4]
            score = result[-2]
            bboxes.append(bbox)
            scores.append(score)

    # Convert bounding box coordinates to format expected by DeepSORT
    bboxes = np.array([xyxy2xywh(bbox) for bbox in bboxes])

    # Track people with DeepSORT
    trackers = deepsort.update(bboxes, scores, frame)

    # Display tracked objects on frame
    for tracker in trackers:
        bbox = tracker.to_tlbr()
        plot_one_box(bbox, frame, label=f'person {tracker.id}')

    # Display frame with bounding boxes
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
