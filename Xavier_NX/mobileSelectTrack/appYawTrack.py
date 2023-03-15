import cv2
import torch
import numpy as np
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from src.rmd_x8 import RMD_X8
import time
from jtop import jtop
import cv2
# import threading



robot = RMD_X8(0x141)
robot.setup()
cam_size = 640
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 5

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')

use_cuda = True
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/', model='yolov5s', source='local').cuda()
model.conf = 0.385
tracker = build_tracker(cfg, use_cuda)
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 30)

#
# cap.set(cv2.CAP_PROP_FPS, 60)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))




highlighted_id = None

app = Flask(__name__)
socketio = SocketIO(app)


def panAngle(angle):
    target = int(angle * 100 * 6)
    bb = target.to_bytes(4, 'little', signed=True)
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.01)


def autoTrack(x1, x2):
    global cam_pan, FRAME_W, angleVector

    trackX = x1
    trackW = x2 - x1
    trackX = trackX + (trackW / 2)
    turn_x = float(trackX - (FRAME_W / 2))
    turn_x /= float(FRAME_W / 2)
    turn_x *= angleVector  # VFOV
    cam_pan += -turn_x
    print('Moving: ', cam_pan - 90)
    cam_pan = max(0, min(180, cam_pan))
    panAngle(int(cam_pan - 90))
    return cam_pan


@app.route('/')
def index():
    return render_template('index.html')


def gen_frames():
    global cap, model, tracker, highlighted_id, outputs, cam_pan  # Add cam_pan to the global variables

    while True:
        ret = cap.grab()
        if not ret:
            continue
        _, frame = cap.retrieve()
        frame_umat = cv2.UMat(frame)
        # frame_umat = cv2.resize(frame_umat, (640, 640))
        frame_umat = cv2.cvtColor(frame_umat, cv2.COLOR_BGR2RGB)
        frame_resized = frame_umat.get()
        results = model(frame_resized, size=640)

        bboxes = results.xywh[0][:, :4].cpu().numpy()
        confidences = results.xywh[0][:, 4].cpu().numpy()
        classes = results.xywh[0][:, 5].cpu().numpy()
        person_indices = np.where(classes == 0)

        try:
            outputs = tracker.update(bboxes[person_indices], confidences[person_indices], classes[person_indices],
                                     frame)
        except ValueError or IndexError:
            print('Lost!')
            continue
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


            cv2.line(frame, (center_x, center_y), (frame_width // 2, frame_height // 2), sight_color, 2)

            if highlighted_id is not None and int(track_id) == highlighted_id:
                color = (0, 0, 255)
                text = f'Selected ID: {int(track_id)}'
                cam_pan = autoTrack(x1, x2)


            else:
                # robot.motor_stop()
                color = (0, 255, 0)
                text = f'Track ID: {int(track_id)}'

            # send_data_update(center_x, center_y, x1, y1, x2, y2,cam_pan - 90)

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


@socketio.on('button_click')
def handle_button_click(data):
    global cam_pan
    angle_change = 5  # Adjust the value to control the angle change per click

    if data['direction'] == 'left':
        cam_pan -= angle_change
    elif data['direction'] == 'right':
        cam_pan += angle_change
    elif data['direction'] == 'bottom':
        cam_pan = 90

    cam_pan = max(0, min(180, cam_pan))  # Ensure the angle is within the valid range
    panAngle(int(cam_pan - 90))

last_sent = 0
update_interval = 2  # Send data every 0.1 seconds
def send_data_update(center_x, center_y, x1, y1, x2, y2, angleInput):
    global last_sent, update_interval

    current_time = time.time()
    if current_time - last_sent < update_interval:
        return

    last_sent = current_time
    x = center_x
    y = center_y
    w = x2 - x1
    h = y2 - y1
    angle = angleInput

    with jtop() as jetson:
        temperature = jetson.temperature

    data = {
        'temperature': temperature['CPU'],
        'motorAngle': angle,
        'x': x,
        'y': y,
        'w': w,
        'h': h
    }
    socketio.emit('data_update', data)


if __name__ == '__main__':
    socketio.run(app, host='192.168.31.177', port=9090, allow_unsafe_werkzeug=True)