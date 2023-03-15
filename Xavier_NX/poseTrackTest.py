import cv2
import numpy as np
import jetson.inference
import jetson.utils

# Load the model
net = jetson.inference.detectNet('ssd-mobilenet-v2', threshold=0.5)

# Create a jetson.utils.cudaDevice() object
cuda_device = jetson.utils.cudaDevice()

# Create a window to display the camera feed and the tracking results
cv2.namedWindow('Object Detection and Tracking', cv2.WINDOW_NORMAL)
cv2.resizeWindow('Object Detection and Tracking', 1280, 720)

# Open the camera
cap = cv2.VideoCapture(0)

# Start the tracking loop
while True:
    # Capture a frame from the camera
    _, frame = cap.read()

    # Move the image to the GPU memory
    img_rgba = cuda_device.Image(frame)

    # Detect objects in the image
    detections = net.Detect(img_rgba)

    # Draw bounding boxes around the detected objects
    for detection in detections:
        x, y, w, h = detection.Left, detection.Top, detection.Width, detection.Height
        cv2.rectangle(frame, (int(x), int(y)), (int(x + w), int(y + h)), (0, 255, 0), 2)
        cv2.putText(frame, net.GetClassDesc(detection.ClassID), (int(x), int(y)), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Move the rendered image from the GPU memory to the CPU memory
    img_rgba = jetson.utils.cudaToNumpy(img_rgba)

    # Display the camera feed and the tracking results
    cv2.imshow('Object Detection and Tracking', frame)

    # Check for key presses
    key = cv2.waitKey(1)
    if key == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
