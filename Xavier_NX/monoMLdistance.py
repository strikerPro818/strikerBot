import torch
import cv2
import numpy as np
from PIL import Image as pil
from monodepth2 import monodepth2

# Load the YOLOv5 model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)

# Enable GPU acceleration for YOLOv5
model.cuda()

# Load the monodepth2 model
mono_model = monodepth2()

# Set camera resolution
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

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

    # Draw bounding boxes around the detected humans and show the x, y, height and width
    boxes = results.xyxy[0].cpu().numpy()
    for box in boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1, y1, x2, y2 = map(int, box[:4])
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            # Draw the bounding box around the detected human
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

            # Get the coordinates of the head
            head_x1, head_y1, head_x2, head_y2 = x1, y1, x2, int(y1 + 0.4 * h)
            # Crop the image to only include the head
            object_img = frame[head_y1:head_y2, head_x1:head_x2]

            # Resize the image to the expected input size of the monodepth2 model
            object_img = cv2.resize(object_img, (mono_model.feed_width, mono_model.feed_height),
                                    interpolation=cv2.INTER_LINEAR)
            object_pil = pil.fromarray(object_img)
            # Convert the image to a PIL image and run the monodepth2 model
            object_pil = pil.fromarray(object_img)
            object_depth = mono_model.eval(object_pil)

            # Convert the color-mapped depth map to grayscale and normalize the pixel values
            object_gray = np.array(object_depth.convert('L')) / 255.0

            # Compute the distance to the object in meters
            object_width = w * sensor_width / 3840
            disparity = np.mean(object_gray)
            distance = focal_length * object_width / disparity

            # Display distance information
            cv2.putText(frame, f'distance: {distance:.2f} m', (x1, y1 - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        2)

    # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
