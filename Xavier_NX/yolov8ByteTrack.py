from ultralytics import YOLO
import cv2
import time

model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
cap = cv2.VideoCapture(1, cv2.CAP_V4L2)

while True:
    # Capture each frame
    ret, frame = cap.read()

    if not ret:
        break

    start_time = time.time()

    # Perform object detection and tracking
    results = model.track(source=frame, show=False, stream=True, tracker="botsort.yaml")

    detection_time = time.time()

    for result in results:
        boxes = result.boxes.xyxy.to("cpu").numpy()
        classes = result.boxes.cls.to("cpu").numpy()
        ids = result.boxes.id.to("cpu").numpy()

        for box, cls, id in zip(boxes, classes, ids):
            if cls == 0:  # "person" class index is 0
                x1, y1, x2, y2 = map(int, box)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)
                cv2.putText(frame, f"ID: {id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Show the annotated frame
    cv2.imshow("YOLO Live Object Detection and Tracking", frame)

    drawing_time = time.time()

    # Calculate and display frame rate and time spent on detection and drawing
    total_time = drawing_time - start_time
    fps = 1 / total_time
    detection_time = detection_time - start_time
    drawing_time = drawing_time - detection_time
    cv2.putText(frame, f"FPS: {fps:.2f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Detection: {detection_time*1000:.2f} ms", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, f"Drawing: {drawing_time*1000:.2f} ms", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Exit the loop if the 'q' key is pressed
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()
