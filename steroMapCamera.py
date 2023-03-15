import cv2
import numpy as np
import torch

# Define camera intrinsics (focal length and principal point) for the stereo camera
focal_length = 2500  # Placeholder value, replace with actual focal length in meters
principal_point = (1280, 720)  # Placeholder value, replace with actual principal point in pixels
baseline = 0.056  # Placeholder value, replace with actual baseline distance in meters

# Initialize stereo matcher
stereo = cv2.StereoBM_create(numDisparities=16, blockSize=15)

# Load YOLOv5 object detection model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)


while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize frame to a smaller size
    # resized_frame = cv2.resize(frame, (360, 180))
    resized_frame = cv2.resize(frame, (1280, 720))


    # Split frame into left and right images
    height, width, channels = resized_frame.shape
    left_img = resized_frame[:, :int(width/2), :]
    right_img = resized_frame[:, int(width/2):, :]

    # Detect humans using YOLOv5 on both left and right images
    left_results = model(left_img)
    right_results = model(right_img)

    # Get the coordinates of the detected humans for both left and right images
    left_boxes = left_results.xyxy[0].cpu().numpy()
    right_boxes = right_results.xyxy[0].cpu().numpy()

    # Draw bounding boxes around the detected humans in both left and right images
    for box in left_boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1_left, y1_left, x2_left, y2_left = map(int, box[:4])
            cv2.rectangle(left_img, (x1_left, y1_left), (x2_left, y2_left), (0, 255, 0), 2)

    for box in right_boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1_right, y1_right, x2_right, y2_right = map(int, box[:4])
            cv2.rectangle(right_img, (x1_right, y1_right), (x2_right, y2_right), (0, 255, 0), 2)

    # Combine left and right images and the disparity map
    # into a single image
    combined_img = np.concatenate((left_img, right_img), axis=1)

    # Compute the disparity map
    disparity = stereo.compute(cv2.cvtColor(left_img, cv2.COLOR_BGR2GRAY),
                               cv2.cvtColor(right_img, cv2.COLOR_BGR2GRAY))

    # Normalize the disparity map to the range [0, 255] for visualization
    disparity_norm = cv2.normalize(disparity, None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8U)
    # Concatenate the disparity map to the combined image
    combined_img = np.concatenate(
        (combined_img, cv2.cvtColor(cv2.resize(disparity_norm, (1280, 720)), cv2.COLOR_GRAY2BGR)), axis=1)

    # Calculate distance to detected humans using stereo triangulation
    for left_box, right_box in zip(left_boxes, right_boxes):
        if left_box[5] == 0 and right_box[5] == 0:  # Class index for humans is 0
            # Calculate the pixel coordinates of the center of the box in both left and right images
            x_left = (left_box[0] + left_box[2]) / 2
            x_right = (right_box[0] + right_box[2]) / 2

            # Calculate the disparity between the center of the box in both left and right images
            disparity_val = disparity_norm[int((left_box[1] + left_box[3]) / 2), int(x_left)]

            if disparity_val > 0:  # Check if disparity value is valid
                # Calculate the depth of the box using stereo triangulation
                depth = (focal_length * baseline) / disparity_val

                # Draw the distance on the image
                distance = round(depth, 2)
                x = round((left_box[0] + right_box[2]) / 2)
                y = round((left_box[1] + left_box[3]) / 2)
                cv2.putText(combined_img, f'{distance}m', (x, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frame
    cv2.imshow('frame', combined_img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

