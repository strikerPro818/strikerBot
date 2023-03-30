import cv2
import numpy as np
import torch
from strongsort import StrongSORT
from pathlib import Path
import torchreid
import time
from ultralytics import YOLO
from PIL import Image

# Load YOLOv5 model
model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')

# model.eval()

# Initialize torchreid model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
reid_model = torchreid.models.build_model(
    name='osnet_x0_25',
    num_classes=1000,
    loss='softmax',
    pretrained=True,
    use_gpu=True
)
reid_model = reid_model.to(device)
reid_model.eval()  # Set model to evaluation mode

# Path to the model weights
# model_weights = "/home/striker/Jetson/osnet_x0_25_imagenet.pt"
model_weights = "/home/striker/Jetson/osnet_x0_25_imagenet.engine"
print('Finished Loading Engine')


# Use FP16 precision if desired (improves performance on some GPUs)
fp16 = True

# Load StrongSORT tracker
tracker = StrongSORT(model_weights=Path(model_weights), device=device, fp16=fp16)

# Open video stream
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
cap.set(cv2.CAP_PROP_FPS, 60)

frame_count = 0
start_time = time.time()
# Initialize human trackers dictionary
human_trackers = {}

# Initialize ID counter
id_counter = 0

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect objects using YOLOv5
    # frame_resized = cv2.resize(frame, (640, 640))
    frame_resized = frame
    results = model(frame_resized,stream=True)
    detections = []

    # detections = results.xyxy[0].cpu()

    img_rgb = cv2.cvtColor(frame_resized, cv2.COLOR_BGR2RGB)
    img_height, img_width, _ = img_rgb.shape
    # detections = detections[(detections[:, 0] >= 0) & (detections[:, 1] >= 0) &
    #                         (detections[:, 2] <= img_width) & (detections[:, 3] <= img_height)]

    for result in results:

        boxes_raw = result.boxes.xyxy.to("cpu")
        classes_raw = result.boxes.cls.to("cpu")
        confidence_raw = result.boxes.conf.to("cpu")
        # print(type(classes), classes.shape)

        for box, cls, conf in zip(boxes_raw, classes_raw, confidence_raw):
            if cls == 0:  # "person" class index is 0
                x1, y1, x2, y2 = map(float, box)
                detections.append([x1, y1, x2, y2, conf.item(), float(cls)])

    if len(detections) > 0:
        detections_tensor = torch.tensor(detections)
        outputs = tracker.update(detections_tensor, frame)
    else:
        outputs = []
    # print(detections_tensor)
    outputs = tracker.update(detections_tensor, frame)
    for output in outputs:
        x1, y1, x2, y2, track_id, _, conf = output

        # Re-identify human using torchreid
        input_image = cv2.cvtColor(frame_resized[int(y1):int(y2), int(x1):int(x2)], cv2.COLOR_BGR2RGB)
        input_image = cv2.resize(input_image, (128, 256))
        input_image = input_image.transpose(2, 0, 1)  # Channels first
        input_image = torch.tensor(input_image, dtype=torch.float32).div(255.0).sub(0.5).div(0.5).unsqueeze(0).to(
            device)
        reid_feature = reid_model(input_image)[0]

        # Draw bounding box and ID label for current human
        color = (255, 0, 0)
        label = str(track_id)
        cv2.rectangle(frame_resized, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(frame_resized, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    # Calculate fps and display as text overlay
    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = frame_count / elapsed_time
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame_resized, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)


        # Display the resulting frame
    cv2.imshow('frame', frame_resized)

    # Increment frame count and update timer
    frame_count += 1
    if frame_count % 10 == 0:  # Calculate fps every 10 frames
        frame_count = 0
        start_time = time.time()

    # Exit if the "q" key is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()