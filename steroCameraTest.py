import torch
import cv2
import numpy as np

# Define camera intrinsics (focal length and principal point) for the stereo camera
# focal_length = 2500  # Placeholder value, replace with actual focal length in meters
focal_length = 850
principal_point = (1280, 720)  # Placeholder value, replace with actual principal point in pixels
# baseline = 0.056  # Placeholder value, replace with actual baseline distance in meters
# baseline = 0.056  # Placeholder value, replace with actual baseline distance in meters
baseline = 0.066  # Placeholder value, replace with actual baseline distance in meters



model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()
# model.conf = 0.5
# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(1, cv2.CAP_V4L2)

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

    # Combine left and right images into a single image
    combined_img = np.concatenate((left_img, right_img), axis=1)

    # Calculate distance to detected humans using stereo triangulation
    for left_box, right_box in zip(left_boxes, right_boxes):
        if left_box[5] == 0 and right_box[5] == 0:  # Class index for humans is 0
            # Calculate the pixel coordinates of the center of the box in both left and right images
            x_left = (left_box[0] + left_box[2]) / 2
            x_right = (right_box[0] + right_box[2]) / 2

            # Calculate the disparity between the center of the box in both left and right images
            disparity = abs(x_left - x_right)

            # Calculate the depth of the box using stereo triangulation
            depth = (focal_length * baseline) / disparity

            # Draw the distance on the image
            distance = round(depth, 2)
            x = round((left_box[0] + right_box[2]) / 2)
            y = round((left_box[1] + left_box[3]) / 2)
            cv2.putText(combined_img, f'{distance}m', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print('distance:',distance)

    # Display the resulting frame
    cv2.imshow('Stereo Vision Track', combined_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()

