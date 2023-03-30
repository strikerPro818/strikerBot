import cv2
import torch
from yolort.runtime import PredictorTRT
from yolort.models import YOLOv5
from yolort.runtime import PredictorORT
from PIL import Image
from torchvision.transforms import ToTensor
import io
from yolort.v5.utils.datasets import LoadImages
batch_size = 1
img_size = 640
size_divisible = 32
fixed_shape = True
score_thresh = 0.35
nms_thresh = 0.45
detections_per_img = 100
# Must upgrade TensorRT to 8.2.4 or higher to use fp16 mode.
precision = "fp16"
img_path = '/home/striker/.local/lib/python3.8/site-packages/yolov5/engineDetect.jpeg'
# safe_download(img_path, img_source)
img_raw = cv2.imread(img_path)
model_path = "/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.pt"

onnx_path = "/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx"


# Load the serialized TensorRT engine
engine_path = "/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.engine"

model = YOLOv5.load_from_yolov5(
    model_path,
    size=(img_size, img_size),
    size_divisible=size_divisible,
    fixed_shape=(img_size, img_size),
    score_thresh=score_thresh,
    nms_thresh=nms_thresh,
)


device = torch.device("cuda")
model = model.eval()
model = model.to(device)
y_runtime = PredictorTRT(engine_path, device=device)
y_runtime.warmup()

predictions = y_runtime.predict("/home/striker/.local/lib/python3.8/site-packages/yolov5/engineDetect.jpeg")