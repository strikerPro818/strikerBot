from ultralytics import YOLO
# model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
model = YOLO('yolov8n-seg.pt')
result = model.predict(source=1,show=True, stream=True)
# results = model.track(source=1, show=True, stream=True, tracker="botsort.yaml")

