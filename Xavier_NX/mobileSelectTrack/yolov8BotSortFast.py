from ultralytics import YOLO
import cv2

# Load a model
model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
results = model.track(source=1, show=False, stream=True, tracker="botsort.yaml")

for result in results:
    img = result.orig_img
    if result.boxes is not None:
        boxes = result.boxes.xyxy.to("cpu").numpy()
        classes = result.boxes.cls.to("cpu").numpy()
        if result.boxes.id is not None:
            ids = result.boxes.id.numpy()
            for box, cls, obj_id in zip(boxes, classes, ids):
                if cls == 0:  # "person" class index is 0
                    x1, y1, x2, y2 = map(int, box)
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw a green rectangle around the person
                    cv2.putText(img, f"ID: {int(obj_id.item())}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                (0, 255, 0), 2)

    cv2.imshow('image', img)
cv2.destroyAllWindows()
