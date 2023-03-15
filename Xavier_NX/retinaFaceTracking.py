import cv2
import numpy as np
from retinaface.RetinaFace import detect_faces
from retinaface.pre_trained_models import get_model

# Load the RetinaFace model
model_name = "resnet50_2020-07-20"
max_size = 2048
model = get_model(model_name, max_size, "cuda:0")
# model.cuda()

# Open the camera feed
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

while True:
    # Capture a frame from the camera
    ret, frame = cap.read()

    # Detect faces in the frame using RetinaFace
    threshold = 0.5
    nms_threshold = 0.4
    faces, landmarks = detect_faces(frame)

    if faces is not None:
        for face in faces:
            if len(face) >= 5:
                x1, y1, x2, y2, score = face[:5]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('RetinaFace', frame)

    # Wait for a key press
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
