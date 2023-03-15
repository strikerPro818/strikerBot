import torch
import cv2
import time
import numpy as np
from flask import Flask, Response, render_template, request

# Load YOLOv5 model from a local directory
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)


# Set the model to run on the Xavier NX with CUDA
model.cuda()

# Initialize the Flask app
app = Flask(__name__)

# Set up the camera capture
cap = cv2.VideoCapture(1)

# Set the camera resolution to 640x480 for faster processing
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Initialize timer variables
prev_time = 0
curr_time = 0

# Initialize the ROI and individual ID lists
rois = []
ids = []

# Define the video stream generator function
def gen():
    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        # Resize the frame to speed up processing
        frame = cv2.resize(frame, (640, 480))

        # Detect humans using YOLOv5
        results = model(frame, size=640)

        # Get the coordinates and class IDs of the detected humans
        boxes = results.xyxy[0].cpu().numpy()
        class_ids = results.pred[0].cpu().numpy()[:, 0]

        # For each detected human, determine which ROI it belongs to and assign an ID
        for i, box in enumerate(boxes):
            if class_ids[i] == 0:  # Class index for humans is 0
                x1, y1, x2, y2 = map(int, box[:4])
                for j, roi in enumerate(rois):
                    if x1 >= roi[0] and y1 >= roi[1] and x2 <= roi[0] + roi[2] and y2 <= roi[1] + roi[3]:
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                        cv2.putText(frame, f'Person {ids[j]}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Convert the frame to JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)

        # Yield the JPEG data as a byte string
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg.tobytes() + b'\r\n')

# Define the index route
@app.route('/')
def index():
    return render_template('index.html')

# Define the video feed route
@app.route('/video_feed')
def video_feed():
    return Response(gen(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Define the ROI selection route
@app.route('/select_roi', methods=['POST'])
def select_roi():
    x, y, w, h = map(int, request.form['roi'].split(','))
    rois.append((x, y, w, h))
    ids.append(len(rois))
    return 'OK'

if __name__ == '__main__':
    # Start the Flask app
    app.run(host='192.168.31.234', port=5000, debug=True)
    cap.release()
    cv2.destroyAllWindows()
    # When the app exits, release the camera
