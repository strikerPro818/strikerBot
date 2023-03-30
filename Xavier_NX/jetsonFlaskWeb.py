from flask import Flask, Response
import jetson_inference as ji
import jetson_utils as ju
import cv2
import numpy as np

app = Flask(__name__)

# Initialize the detection network and camera
net = ji.detectNet("ped-100", threshold=0.5)
camera = ju.videoSource("/dev/video0")
# camera = ju.videoSource("v4l2:///dev/video4")
font = ju.cudaFont()


def draw_boxes(img, detections):
    for detection in detections:
        if detection.ClassID == 1:
            left = int(detection.Left)
            top = int(detection.Top)
            right = int(detection.Right)
            bottom = int(detection.Bottom)
            ju.cudaDrawRect(img, (left, top, right, bottom), (0, 255, 0, 255))

def generate_frames():
    while True:
        # Capture a frame from the camera
        img = camera.Capture()

        # Perform object detection on the frame
        detections = net.Detect(img)

        # Draw boxes around the detected objects
        # draw_boxes(img, detections)
        # ju.cudaOverlay(img,'fuck')


        # Convert the cudaImage object to a numpy array
        img_np = ju.cudaToNumpy(img)

        # Convert the image to BGR colorspace for use with OpenCV
        img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

        # Perform some processing on the numpy array here...
        # For example, you could apply a filter or resize the image.

        # Convert the numpy array back to a JPEG byte stream
        ret, buffer = cv2.imencode('.jpg', img_np)
        frame = buffer.tobytes()

        # Yield the frame as a Flask response
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
@app.route('/')
def index():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run(host='192.168.31.177', port=9090, debug=True)

# Release resources
camera.Close()
