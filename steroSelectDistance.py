import torch
import cv2
import numpy as np

# Define camera intrinsics (focal length and principal point) for the stereo camera
# focal_length = 2500  # Placeholder value, replace with actual focal length in meters
focal_length = 1000
principal_point = (1280, 720)  # Placeholder value, replace with actual principal point in pixels
# baseline = 0.056  # Placeholder value, replace with actual baseline distance in meters
# baseline = 0.056  # Placeholder value, replace with actual baseline distance in meters
baseline = 0.067  # Placeholder value, replace with actual baseline distance in meters



model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Select person to track
selected_id = -1
selected_box = None
tracker = cv2.TrackerCSRT_create()

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Split frame into left and right images
    height, width, channels = frame.shape
    left_img = frame[:, :int(width/2), :]
    right_img = frame[:, int(width/2):, :]

    # Detect humans using YOLOv5 on both left and right images
    left_results = model(left_img, size=640)
    right_results = model(right_img, size=640)

    # Get the coordinates of the detected humans for both left and right images
    left_boxes = left_results.xyxy[0].cpu().numpy()
    right_boxes = right_results.xyxy[0].cpu().numpy()

    # Draw bounding boxes around the detected humans in both left and right images
    for box in left_boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1_left, y1_left, x2_left, y2_left = map(int, box[:4])
            cv2.rectangle(left_img, (x1_left, y1_left), (x2_left, y2_left), (0, 255, 0), 2)
            x_left, y_left, w_left, h_left = x1_left, y1_left, x2_left - x1_left, y2_left - y1_left
            cv2.putText(left_img, f'x:{x_left}, y:{y_left}, w:{w_left}, h:{h_left}', (x1_left, y1_left-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    for box in right_boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1_right, y1_right, x2_right, y2_right = map(int, box[:4])
            cv2.rectangle(right_img, (x1_right, y1_right), (x2_right, y2_right), (0, 255, 0), 2)
            x_right, y_right, w_right, h_right = x1_right, y1_right, x2_right - x1_right, y2_right - y1_right
            cv2.putText(right_img, f'x:{x_right}, y:{y_right}, w:{w_right}, h:{h_right}', (x1_right, y1_right-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Combine left and
    combined_img = np.concatenate((left_img, right_img), axis=1)

    # Select the first detected human from the left image
    selected_box = None
    for box in left_boxes:
        if box[5] == 0:  # Class index for humans is 0
            selected_box = box
            break

    if selected_box is not None:
        # Calculate the pixel coordinates of the center of the selected box in both left and right images
        x1_left, y1_left, x2_left, y2_left = map(int, selected_box[:4])
        x_left_center = (x1_left + x2_left) / 2
        y_left_center = (y1_left + y2_left) / 2
        x_right_center = x_left_center - disparity

        # Calculate the disparity between the center of the selected box in both left and right images
        disparity = abs(x_left_center - x_right_center)

        # Calculate the depth of the selected box using stereo triangulation
        depth = (focal_length * baseline) / disparity

        # Draw the distance on the image
        distance = round(depth, 2)
        cv2.putText(combined_img, f'{distance}m', (x1_left, y1_left - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                    2)
        print('distance:', distance)

        # Draw bounding box around the selected human in both left and right images
        cv2.rectangle(left_img, (x1_left, y1_left), (x2_left, y2_left), (0, 255, 0), 2)
        cv2.rectangle(right_img, (int(x_right_center), y1_left), (int(x_right_center) + (x2_left - x1_left), y2_left),
                      (0, 255, 0), 2)

        # Draw center point of the selected human in both left and right images
        cv2.circle(left_img, (int(x_left_center), int(y_left_center)), 3, (0, 255, 0), -1)
        cv2.circle(right_img, (int(x_right_center), int(y_left_center)), 3, (0, 255, 0), -1)

    # Display the resulting frame
    cv2.imshow('Stereo Vision Track', combined_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
cap.release()
cv2.destroyAllWindows()
