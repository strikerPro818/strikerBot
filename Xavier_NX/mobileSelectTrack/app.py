import cv2
import torch
import numpy as np
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
import time

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')

use_cuda = True
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/',model='yolov5s',source='local').cuda()
tracker = build_tracker(cfg, use_cuda)
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

highlighted_id = None

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

def gen_frames():
    global cap, model, tracker, highlighted_id, outputs  # Add outputs to the global variables

    while True:
        ret, frame = cap.read()
        results = model(frame, size=640)
        bboxes = results.xywh[0][:, :4].cpu().numpy()
        confidences = results.xywh[0][:, 4].cpu().numpy()
        classes = results.xywh[0][:, 5].cpu().numpy()
        person_indices = np.where(classes == 0)
        outputs = tracker.update(bboxes[person_indices], confidences[person_indices], classes[person_indices], frame)

        frame_height, frame_width = frame.shape[:2]
        scope_thickness = 2
        scope_color = (0, 0, 255)
        cv2.line(frame, (0, frame_height // 2), (frame_width, frame_height // 2), scope_color, scope_thickness)
        cv2.line(frame, (frame_width // 2, 0), (frame_width // 2, frame_height), scope_color, scope_thickness)

        for output in outputs:
            x1, y1, x2, y2, _, track_id = output
            w, h = x2 - x1, y2 - y1
            center_x, center_y = x1 + w // 2, y1 + h // 2

            sight_width = int(w * 0.2)
            sight_thickness = int(w * 0.005)

            if highlighted_id is not None and int(track_id) == highlighted_id:
                sight_color = (0, 0, 255)
            else:
                sight_color = (0, 255, 0)

            cv2.rectangle(frame, (center_x - sight_width // 2, center_y - sight_thickness // 2),
                          (center_x + sight_thickness // 2, center_y + sight_width // 2), sight_color, -1)
            cv2.circle(frame, (center_x, center_y), sight_width // 2, sight_color, sight_thickness)
            cv2.line(frame, (center_x, center_y), (frame_width // 2, frame_height // 2), sight_color, 2)

            if highlighted_id is not None and int(track_id) == highlighted_id:
                color = (0, 0, 255)
                text = f'Selected ID: {int(track_id)}'
            else:
                color = (0, 255, 0)
                text = f'Track ID: {int(track_id)}'

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        _, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

outputs = []

@socketio.on('click_event')
def handle_click_event(data):
    global highlighted_id, outputs
    x, y = data['x'], data['y']

    found_id = None
    for output in outputs:
        x1, y1, x2, y2, _, track_id = output
        if x1 <= x <= x2 and y1 <= y <= y2:
            found_id = int(track_id)
            break

    if highlighted_id is not None and highlighted_id == found_id:
        highlighted_id = None
    else:
        highlighted_id = found_id


if __name__ == '__main__':
    socketio.run(app, host='192.168.31.177', port=9090,allow_unsafe_werkzeug=True)
