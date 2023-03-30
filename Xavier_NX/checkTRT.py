import sys
import onnx
filename = '/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx'
model = onnx.load(filename)
onnx.checker.check_model(model)