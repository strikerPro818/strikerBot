import numpy as np
from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from src.rmd_x8 import RMD_X8
from jtop import jtop

from turbojpeg import TurboJPEG, TJPF_BGR, TJFLAG_FASTDCT

from strongsort.utils.parser import get_config
from ultralytics import YOLO

import cv2

import torch
from strongsort import StrongSORT
from pathlib import Path
import torchreid
import time
import cProfile

#
# model = torch.hub.load(r'/home/striker/.local/lib/python3.8/site-packages/yolov5/', 'custom',
#                        path=r'/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.engine',
#                        source='local').cuda()
model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')

# model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.pt")
# model = torch.hub.load(r'/home/striker/.local/lib/python3.8/site-packages/yolov5/', 'custom',
#                        path=r'/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine',
#                        source='local').cuda()

turboJPG = TurboJPEG()

robot = RMD_X8(0x141)
robot.setup()
cam_size = 640
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 5

# Initialize torchreid model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
reid_model = torchreid.models.build_model(
    name='osnet_x0_25',
    num_classes=1000,
    loss='softmax',
    pretrained=True,
    use_gpu=True
)
reid_model = reid_model.to(device)
reid_model.eval()  # Set model to evaluation mode

# Path to the model weights
model_weights = "/home/striker/Jetson/osnet_x0_25_imagenet.engine"

# Use FP16 precision if desired (improves performance on some GPUs)
fp16 = True

cfg = get_config('/home/striker/Jetson/Xavier_NX/mobileSelectTrack/strong_sort.yaml')


# Load StrongSORT tracker
tracker = StrongSORT(model_weights=Path(model_weights), device=device, fp16=fp16)
# tracker = StrongSORT(model_weights=Path(model_weights), device='cuda:0', fp16=fp16,max_dist=cfg.STRONGSORT.MAX_DIST,
#                      max_iou_distance=cfg.STRONGSORT.MAX_IOU_DISTANCE, max_age=cfg.STRONGSORT.MAX_AGE,n_init=cfg.STRONGSORT.N_INIT,nn_budget=cfg.STRONGSORT.NN_BUDGET,mc_lambda=cfg.STRONGSORT.MC_LAMBDA,
#                      ema_alpha=cfg.STRONGSORT.EMA_ALPHA)

cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
cap.set(cv2.CAP_PROP_FPS, 60)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 160)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 160)
# cap.set(cv2.CAP_PROP_BUFFERSIZE, 30)

#
# cap.set(cv2.CAP_PROP_FPS, 60)
# cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))


highlighted_id = None
selected_reid_feature = None
reid_feature = None

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

def dot_product_similarity(feature1, feature2):
    norm1 = torch.norm(feature1)
    norm2 = torch.norm(feature2)
    return torch.dot(feature1, feature2) / (norm1 * norm2)
def gen_frames():
    global cap, model, tracker, reid_model, highlighted_id, outputs, cam_pan, device
    similarity_threshold = 0.85

    while True:
        ret = cap.grab()
        if not ret:
            continue
        _, frame = cap.retrieve()
        # display_frame = np.copy(frame)
        frame_resized = frame

        results = model.predict(frame, stream=True)
        detections = []


        for result in results:

            boxes_raw = result.boxes.xyxy.to("cpu")
            classes_raw = result.boxes.cls.to("cpu")
            confidence_raw = result.boxes.conf.to("cpu")
            # print(type(classes), classes.shape)

            for box, cls, conf in zip(boxes_raw, classes_raw, confidence_raw):
                if cls == 0:  # "person" class index is 0
                    x1, y1, x2, y2 = map(float, box)
                    detections.append([x1, y1, x2, y2, conf.item(), float(cls)])

        if len(detections) > 0:
            detections_tensor = torch.tensor(detections)
            outputs = tracker.update(detections_tensor, frame)
        else:
            outputs = []

        outputs = tracker.update(detections_tensor, frame)

        for output in outputs:
            x1, y1, x2, y2, track_id, _, conf = output

            # Re-identify human using torchreid
            input_image = cv2.cvtColor(frame_resized[int(y1):int(y2), int(x1):int(x2)], cv2.COLOR_BGR2RGB)
            input_image = cv2.resize(input_image, (128, 256))
            input_image = input_image.transpose(2, 0, 1)
            input_image = torch.tensor(input_image, dtype=torch.float32).div(255.0).sub(0.5).div(0.5).unsqueeze(0).to(device)
            reid_feature = reid_model(input_image)[0]

            if selected_reid_feature is not None:
                similarity = dot_product_similarity(reid_feature, selected_reid_feature)
                if similarity > similarity_threshold:
                    track_id = highlighted_id

            if highlighted_id is not None and int(track_id) == highlighted_id:
                color = (0, 0, 255)
                text = f'Selected ID: {int(track_id)}'
                cam_pan = autoTrack(x1, x2)
            else:
                color = (0, 255, 0)
                text = f'Track ID: {int(track_id)}'

            cv2.rectangle(frame_resized, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
            cv2.putText(frame_resized, text, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        encoded_image = turboJPG.encode(frame_resized, quality=80, pixel_format=TJPF_BGR, flags=TJFLAG_FASTDCT)
        # encoded_image = turboJPG.encode(display_frame, quality=80, pixel_format=TJPF_BGR, flags=TJFLAG_FASTDCT)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n\r\n')




@app.route('/video_feed')
def video_feed():
    pr = cProfile.Profile()
    pr.enable()
    frames = gen_frames()
    pr.disable()
    pr.print_stats(sort='cumtime')
    return Response(frames, content_type='multipart/x-mixed-replace; boundary=frame')
# def video_feed():
#     return Response(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')



outputs = []


@socketio.on('click_event')
def handle_click_event(data):
    global highlighted_id, outputs
    x, y = data['x'], data['y']

    found_id = None
    for output in outputs:
        x1, y1, x2, y2, track_id, _, conf = output
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


# if __name__ == '__main__':
#     socketio.run(app, host='192.168.31.177', port=9090, allow_unsafe_werkzeug=True)

if __name__ == '__main__':
    socketio.run(app, host='192.168.31.177', port=9090, allow_unsafe_werkzeug=True)
    robot.motor_stop()
    # t = threading.Thread(target=gen_frames)
    # t.start()
    # s =threading.Thread(target=send_data_update())
    # s.start()
