import torch
import cv2
import math

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)

# Enable GPU acceleration
model.cuda()

# Set camera resolution
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 3840)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 2160)

# Define camera intrinsic parameters
focal_length = 2.26  # mm
fov = 130  # degrees
sensor_width = 3.68  # mm
sensor_height = 2.76  # mm

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Detect humans using YOLOv5
    results = model(frame, size=640)

    # Get the coordinates of the detected humans
    boxes = results.xyxy[0].cpu().numpy()

    # Draw bounding boxes around the detected humans and show the x, y, height and width
    for box in boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            cv2.putText(frame, f'x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

            # Calculate distance to object in meters
            object_width = w * sensor_width / 3840
            distance = focal_length * object_width / math.tan(math.radians(fov/2))

            # Display distance information
            cv2.putText(frame, f'distance: {distance:.2f} m', (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
