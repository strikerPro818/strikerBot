import cv2
import torch
from deep_sort import DeepSort
from src.rmd_x8 import RMD_X8
from yolov5_detect import detect  # Function to detect objects using YOLOv5
import numpy as np

robot = RMD_X8(0x141)
robot.setup()

cam_size = 1600
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 15

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()
model.conf = 0.38

# Initialize the deepsort tracker
tracker = DeepSort("deep_sort/deep/checkpoint/ckpt.t7")

# Initialize the object IDs
object_ids = {}

# Initialize the object count
object_count = 0

# Open the video capture device
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_size)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_size)

# Create a CUDA GpuMat object for the grayscale image
gray_gpu = cv2.cuda_GpuMat()

def panAngle(angle):
    target = int(angle * 100 * 6);
    bb = target.to_bytes(4, 'little', signed=True)
    print()
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame_height, frame_width = frame.shape[:2]

    # Detect objects using YOLOv5
    results = detect(model, frame, conf_thres=0.5, iou_thres=0.45)

    # Get the boxes and scores of the detected objects
    boxes = results.xyxy[0].cpu().numpy()
    scores = results.xyxy[0][:, 4].cpu().numpy()

    # Apply non-maximum suppression to remove redundant detections
    indices = cv2.dnn.NMSBoxes(boxes, scores, 0.5, 0.4)

    # Create an array to store the detections
    detections = []

    # Loop over the indices
    for i in indices:
        # Get the index of the detection
        i = i[0]

        # Get the coordinates of the bounding box
        x, y, w, h = boxes[i, :]

        # Convert the coordinates to integers
        x, y, w, h = int(x), int(y), int(w), int(h)

        # Get the ID of the object
        if i not in object_ids:
            object_ids[i] = object_count
            object_count += 1
        object_id = object_ids[i]

        # Add the detection to the array
        detections.append([x, y, w, h, object_id])

    # Convert the detections to a numpy array
    detections = np.array(detections)

    # Pass the detections to the deepsort tracker
    outputs = tracker.update(detections)

    # Draw a red scope to divide the frame into four sections
    scope_thickness = 2
    scope_color = (0, 0, 255)
    cv2.line(frame, (0, frame_height // 2), (frame_width, frame_height // 2), scope_color, scope_thickness)
    cv2.line(frame, (frame_width // 2, 0), (frame_width // 2, frame_height), scope_color, scope_thickness)

    # Loop over the outputs
    for output in outputs:
        # Get the bounding box and ID of the object
        x, y, w, h, object_id = output[:5]

        # Draw the bounding box and ID of the object
        color = (0, 255, 0)
        thickness = 2
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        cv2.putText(frame, f'ID:{object_id}', (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, thickness)

        # Move the camera to center the bounding box
        trackX = x
        trackW = w
        trackX = trackX + (trackW / 2)
        turn_x = float(trackX - (FRAME_W / 2))
        turn_x /= float(FRAME_W / 2)
        turn_x *= angleVector  # VFOV
        cam_pan += -turn_x
        cam_pan = max(0, min(180, cam_pan))
        panAngle(int(cam_pan - 90))

        # Draw a line from the center of the bounding box to the center of the frame
        center_x, center_y = x + w // 2, y + h // 2
        cv2.line(frame, (center_x, center_y), (frame_width // 2, frame_height // 2), (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        robot.motor_stop()
        break

# Release the capture device and destroy the windows
cap.release()
cv2.destroyAllWindows()
robot.motor_stop()
