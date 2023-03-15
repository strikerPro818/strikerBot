import cv2
import numpy as np
import torch

# Load the pre-trained YOLOv5 object detection model with CUDA support
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True).cuda().eval()

# Initialize the video capture using the onboard camera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"YUYV"))

# Set the resolution to 640x480
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Loop over the frames from the video capture
while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # If the frame fails to capture, break the loop
    if not ret:
        break

    # Convert the frame to a Torch tensor with 4 dimensions
    tensor = torch.from_numpy(frame.transpose((2, 0, 1))).to('cuda').float().div(255).unsqueeze(0)

    # Apply the YOLOv5 object detection model to the tensor
    detections = model(tensor, size=640)

    # Get the detected people as a Torch tensor
    people = detections.pred[detections.pred[:, 5] == 0]

    # Loop over the detected people and draw bounding boxes around them
    for person in people:
        bbox = person[:4].detach().cpu().numpy()
        score = person[4].detach().cpu().numpy()
        cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
        cv2.putText(frame, f'{score:.2f}', (bbox[0], bbox[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('People Tracking', frame)

    # Exit the loop if the user presses the 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()
