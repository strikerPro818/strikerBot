import cv2
import numpy as np
from deepSortPlayGround.deep_sort import build_tracker

# Load YOLOv5 model
model = cv2.dnn.readNet("yolov5.weights", "yolov5.cfg")

# Load classes
with open("coco.names", "r") as f:
    classes = [line.strip() for line in f.readlines()]

# Initialize Deep SORT tracker
tracker = build_tracker("deep_sort/configs/deep_sort.yaml")

# Open video capture
cap = cv2.VideoCapture("test_video.mp4")

# Loop through frames
while True:
    # Read frame
    ret, frame = cap.read()
    if not ret:
        break

    # Perform YOLOv5 object detection
    blob = cv2.dnn.blobFromImage(frame, 1/255.0, (416, 416), swapRB=True)
    model.setInput(blob)
    outputs = model.forward(model.getUnconnectedOutLayersNames())
    boxes = []
    confidences = []
    class_ids = []
    for output in outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0] * frame.shape[1])
                center_y = int(detection[1] * frame.shape[0])
                width = int(detection[2] * frame.shape[1])
                height = int(detection[3] * frame.shape[0])
                left = int(center_x - width/2)
                top = int(center_y - height/2)
                boxes.append([left, top, width, height])
                confidences.append(float(confidence))
                class_ids.append(class_id)

    # Perform object tracking with Deep SORT
    detections = np.array(boxes)
    confidences = np.array(confidences)
    detections[:, 2:] += detections[:, :2]  # convert to (left, top, right, bottom)
    trackers = tracker.update(detections, confidences, frame)

    # Draw bounding boxes and labels
    for track in trackers:
        left, top, right, bottom, track_id = track
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, f"ID: {track_id}", (left, top - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display frame
    cv2.imshow("Object Tracking", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
