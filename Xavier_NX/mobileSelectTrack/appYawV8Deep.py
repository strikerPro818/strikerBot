import numpy as np
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from src.rmd_x8 import RMD_X8
import time
from jtop import jtop
import cv2
from ultralytics import YOLO

from turbojpeg import TurboJPEG, TJPF_BGR, TJFLAG_FASTDCT

turboJPG = TurboJPEG()

robot = RMD_X8(0x141)
robot.setup()
cam_size = 640
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 5
model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')

use_cuda = True

tracker = build_tracker(cfg, use_cuda)
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))

cap.set(cv2.CAP_PROP_FPS, 60)

highlighted_id = None

app = Flask(__name__)
socketio = SocketIO(app)

deepsortConfig = {
    'max_cosine_distance': 0.2,
    'nn_budget': 100,
    'max_iou_distance': 0.7,
    'max_age': 30,
    'n_init': 3
}


def panAngle(angle):
    target = int(angle * 100 * 6)
    bb = target.to_bytes(4, 'little', signed=True)
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)
    # time.sleep(0.01)


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
    # return render_template('index.html')
    return render_template('simpleIndex.html')



def gen_frames():
    global cap, model, tracker, highlighted_id, outputs, cam_pan  # Add cam_pan to the global variables

    while True:
        ret = cap.grab()
        if not ret:
            continue
        _, frame = cap.retrieve()

        frame_resized = frame

        results = model.predict(frame_resized, stream=True)

        boxes = []
        scores = []
        classes = []
        for result in results:
            boxes.extend(result.boxes.xywh.to("cpu").numpy())
            scores.extend(result.boxes.conf.to("cpu").numpy())
            classes.extend(result.boxes.cls.to("cpu").numpy())

        # Convert lists to NumPy arrays
        boxes = np.array(boxes)
        scores = np.array(scores)
        classes = np.array(classes)

        try:
            # Update the tracker with the detected boxes, scores, and classes
            if len(boxes) > 0:
                outputs = tracker.update(boxes, scores, classes, frame_resized)
            else:
                outputs = []

        except ValueError or IndexError:
            print('Lost!')
            continue

        frame_height, frame_width = frame_resized.shape[:2]
        scope_thickness = 2
        scope_color = (0, 0, 255)
        cv2.line(frame_resized, (0, frame_height // 2), (frame_width, frame_height // 2), scope_color, scope_thickness)
        cv2.line(frame_resized, (frame_width // 2, 0), (frame_width // 2, frame_height), scope_color, scope_thickness)

        for x1, y1, x2, y2, cls, track_id in outputs:
            if cls == 0:  # "person" class index is 0
                cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), thickness=2)
                cv2.putText(frame_resized, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                w, h = x2 - x1, y2 - y1
                center_x, center_y = x1 + w // 2, y1 + h // 2

                sight_width = int(w * 0.2)
                sight_thickness = int(w * 0.005)

                if highlighted_id is not None and int(track_id) == highlighted_id:
                    sight_color = (0, 0, 255)
                else:
                    sight_color = (0, 255, 0)

                cv2.rectangle(frame_resized, (center_x - sight_width // 2, center_y - sight_thickness // 2),
                              (center_x + sight_thickness // 2, center_y + sight_width // 2), sight_color, -1)

                cv2.line(frame_resized, (center_x, center_y), (frame_width // 2, frame_height // 2), sight_color, 2)

                if highlighted_id is not None and int(track_id) == highlighted_id:
                    color = (0, 0, 255)
                    text = f'Selected ID: {int(track_id)}'
                    cam_pan = autoTrack(x1, x2)


                else:
                    # robot.motor_stop()
                    color = (0, 255, 0)
                    text = f'Track ID: {int(track_id)}'
                    # robot.motor_stop()

                cv2.rectangle(frame_resized, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame_resized, text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        encoded_image = turboJPG.encode(frame_resized, quality=80, pixel_format=TJPF_BGR, flags=TJFLAG_FASTDCT)

        # send the encoded image over the network
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n\r\n')


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
update_interval = 10  # Send data every 0.1 seconds


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
    robot.motor_stop()
