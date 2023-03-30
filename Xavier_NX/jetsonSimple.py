from sys import argv

import jetson_inference as ji
import jetson_utils as ju
import time
from jetson_utils import cudaFont
import argparse



def draw_boxes(img, detections):
    for detection in detections:
        if detection.ClassID == 1:
            left = int(detection.Left)
            top = int(detection.Top)
            right = int(detection.Right)
            bottom = int(detection.Bottom)
            # ju.cudaDrawRect(img, (left, top, right, bottom), (0, 255, 0, 255))
            ju.cudaDrawRect(img, (left, top, right, bottom), font.Gray40)


# Initialize the detection network, camera and display
net = ji.detectNet("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.engine", threshold=0.5)
# net = ji.detectNet("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx",argv=[ '--input-blob=input_0 --output-cvg=scores --output-bbox=boxes'])
# net = ji.detectNet("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx",argv=[ '--output-bbox=boxes'])
# net = ji.detectNet("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx",argv=['-- output-bbox=boxes'])
# net = ji.detectNet(argv['--model=/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.onnx', ' --input-blob=input_0', ' --output-cvg=scores', ' --output-bbox=boxes'])



camera = ju.videoSource("v4l2:///dev/video4")
display = ju.videoOutput("display://0")



# Initialize CUDA Font object for FPS display
font = cudaFont()

while display.IsStreaming():
    # Capture a frame from the camera
    img = camera.Capture()

    # Perform object detection on the frame
    detections = net.Detect(img)

    # Draw boxes around the detected objects
    draw_boxes(img, detections)

    # Calculate and display FPS on the screen
    display.SetStatus("{:s} | Network {:.0f} FPS".format('PedNet', net.GetNetworkFPS()))
    # print out performance info
    net.PrintProfilerTimes()

    # Display the frame on the screen

    display.Render(img)

# Release resources
camera.Close()
display.Close()
