import cv2
from ultralytics import YOLO
import time

model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
frame_count = 0
start_time = time.time()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    results = model.predict(frame, stream=True)

    for result in results:
        boxes = result.boxes.xyxy.to("cpu").numpy()
        classes = result.boxes.cls.to("cpu").numpy()

        for box, cls in zip(boxes, classes):
            if cls == 0:  # "person" class index is 0
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)

    # Display the resulting frame

    # Calculate fps and display as text overlay
    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = frame_count / elapsed_time
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('frame', frame)

    frame_count += 1
    if frame_count % 10 == 0:  # Calculate fps every 10 frames
        frame_count = 0
        start_time = time.time()

    cv2.imshow('frame', frame)

    # Exit if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
cap.release()
cv2.destroyAllWindows()
