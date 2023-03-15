import torch
import cv2

model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()

cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

object_ids = {}  # Dictionary to store object ids
id_count = 0  # Counter for object ids

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

            # Check if the object is already being tracked
            object_id = None
            for i in object_ids.keys():
                if abs(x - object_ids[i][0]) <= w and abs(y - object_ids[i][1]) <= h:
                    object_id = i
                    break

            # If the object is new, assign it a new id
            if object_id is None:
                object_id = id_count
                id_count += 1
                object_ids[object_id] = (x, y)

            # Draw the object id on the bounding box
            cv2.putText(frame, f'ID: {object_id}', (x1, y1-30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            object_ids[object_id] = (x, y)

    # Display the resulting frame
    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
