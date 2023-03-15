import torch
import cv2
import numpy as np

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Initialize a counter for assigning ids
id_counter = 0

# Initialize a dictionary to store the ids and bounding boxes of detected humans
human_dict = {}

# Initialize the id of the currently selected human to None
selected_id = None

# Initialize the previous position of the selected human to None
prev_pos = None

# Initialize the optical flow object
lk_params = dict(winSize=(15, 15), maxLevel=2, criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

def mouse_callback(event, x, y, flags, param):
    global selected_id, mouse_x, mouse_y
    if event == cv2.EVENT_LBUTTONDOWN:
        for human_id, bbox in human_dict.items():
            if (x >= bbox[0]) and (x <= bbox[2]) and (y >= bbox[1]) and (y <= bbox[3]):
                # A human's bounding box was clicked, so select it for tracking
                selected_id = human_id
                break

# Set up the mouse callback function
cv2.namedWindow('frame')
cv2.setMouseCallback('frame', mouse_callback)

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

            # Check if this human has already been detected
            found = False
            for human_id, bbox in human_dict.items():
                if (x1 >= bbox[0]) and (x2 <= bbox[2]) and (y1 >= bbox[1]) and (y2 <= bbox[3]):
                    # This human has already been detected, so update the bounding box
                    human_dict[human_id] = (x1, y1, x2, y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    x, y, w, h = x1, y1, x2 - x1, y2 - y1
                    cv2.putText(frame, f'id:{human_id}, x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                    found = True
                    break

            if not found:
                # This is a new human, so assign a new id
                human_dict[id_counter] = (x1, y1, x2, y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # Show the current frame with bounding boxes and labels
            cv2.imshow('frame', frame)

            # Wait for a key press
            key = cv2.waitKey(1) & 0xFF

            # If the 'q' key is pressed, exit the loop
            if key == ord('q'):
                break

            # If a human is selected for tracking, update its position
            if selected_id is not None:
                if selected_id in human_dict:
                    bbox = human_dict[selected_id]
                    x1, y1, x2, y2 = bbox
                    prev_pos = (int((x1 + x2) / 2), int((y1 + y2) / 2))
                    # Print the current selected id and its xy width height
                    print(f"Selected ID: {selected_id}")
                    print(f"x: {x1}, y: {y1}, width: {x2 - x1}, height: {y2 - y1}")

                    cv2.circle(frame, prev_pos, 5, (0, 255, 255), -1)

                    # Draw a rectangle around the selected human
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

                    # Show the id of the selected human
                    cv2.putText(frame, f'Selected human: {selected_id}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 0, 255), 2)

                # Clear the selection if the 'c' key is pressed
                if key == ord('c'):
                    selected_id = None

            # If no human is selected for tracking, check if the mouse has clicked on a human
            else:
                if len(human_dict) > 0:
                    for human_id, bbox in human_dict.items():
                        x1, y1, x2, y2 = bbox
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        x, y, w, h = x1, y1, x2 - x1, y2 - y1
                        cv2.putText(frame, f'id:{human_id}, x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1 - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)

                        # Check if this human's bounding box was clicked
                        if (key == ord('c')) and (x1 <= mouse_x <= x2) and (y1 <= mouse_y <= y2):
                            # Clear the selection
                            selected_id = human_id
                            break

            # Increment the id counter
    id_counter += 1
cap.release()
cv2.destroyAllWindows()