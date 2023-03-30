import jetson_inference as ji
import jetson_utils as ju

def draw_boxes(img, detections):
    for detection in detections:
        if detection.ClassID == 1:
            # x1, y1, x2, y2 = int(detection.Left), int(detection.Top), int(detection.Right), int(detection.Bottom)
            left = int(detection.Left)
            top = int(detection.Top)
            right = int(detection.Right)
            bottom = int(detection.Bottom)
            ju.cudaDrawRect(img, (left, top, right, bottom), (0, 255, 0, 255))



net = ji.detectNet("ssd-mobilenet-v2", threshold=0.5)
camera = ju.videoSource("v4l2:///dev/video2")
display = ju.videoOutput("display://0")

while display.IsStreaming():
    img = camera.Capture()
    detections = net.Detect(img)
    draw_boxes(img, detections)
    display.Render(img)
