from flask import Flask, render_template, Response
from flask_socketio import SocketIO, emit
from src.rmd_x8 import RMD_X8
from jtop import jtop
import cv2
from turbojpeg import TurboJPEG, TJPF_BGR, TJFLAG_FASTDCT
import time
from ultralytics import YOLO
import Jetson.GPIO as GPIO

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)
shooter = GPIO.PWM(33, 100)
shooter.start(0)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(32, GPIO.OUT)
feeder = GPIO.PWM(32, 100)
feeder.start(0)

model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
results = model.track(source=0, show=False, stream=True, tracker="botsort.yaml")


turboJPG = TurboJPEG()
robot = RMD_X8(0x141)
robot.setup()
cam_size = 640
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 7


highlighted_id = None
selected_reid_feature = None
reid_feature = None
latest_result = None
app = Flask(__name__)
socketio = SocketIO(app)

def startShooter(speed):
    print('Shooter Current Speed:', speed)
    shooter.ChangeDutyCycle(speed)
def stopShooter():
    print('Shooter Stopped')
    shooter.ChangeDutyCycle(0)

def startFeeder(speed):
    print('Shooter Current Speed:', speed)
    feeder.ChangeDutyCycle(speed)
def stopFeeder():
    print('Feeder Stopped')
    feeder.ChangeDutyCycle(0)

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
    global results, model, tracker, reid_model, outputs, cam_pan, device, latest_result

    for result in results:
        img = result.orig_img
        latest_result = result
        # print(img)
        if result.boxes is not None:
            boxes = result.boxes.xyxy.to("cpu").numpy()
            classes = result.boxes.cls.to("cpu").numpy()
            if result.boxes.id is not None:
                ids = result.boxes.id.numpy()
                for box, cls, obj_id in zip(boxes, classes, ids):
                    if cls == 0:  # "person" class index is 0
                        x1, y1, x2, y2 = map(int, box)
                        w, h = x2 - x1, y2 - y1
                        center_x, center_y = x1 + w // 2, y1 + h // 2
                        track_id = int(obj_id.item())

                        if highlighted_id is not None and track_id == highlighted_id:
                            color = (0, 0, 255)
                            text = f'Selected ID: {int(track_id)}'
                            cam_pan = autoTrack(x1, x2)
                        else:
                            color = (0, 255, 0)
                            text = f'Track ID: {int(track_id)}'

                        cv2.rectangle(img, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
                        cv2.putText(img, text, (int(x1), int(y1) - 10),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
                        # send_data_update(center_x, center_y, x1, y1, x2, y2,cam_pan - 90)

        encoded_image = turboJPG.encode(img, quality=80, pixel_format=TJPF_BGR, flags=TJFLAG_FASTDCT)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + encoded_image + b'\r\n\r\n')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), content_type='multipart/x-mixed-replace; boundary=frame')

@socketio.on('connect')
def on_connect():
    print("Client connected")

@socketio.on('click_event')
def handle_click_event(data):
    global highlighted_id, latest_result
    x, y = data['x'], data['y']

    found_id = None
    if latest_result is not None:
        boxes = latest_result.boxes.xyxy.to("cpu").numpy()
        classes = latest_result.boxes.cls.to("cpu").numpy()
        ids = latest_result.boxes.id.numpy()
        for box, cls, obj_id in zip(boxes, classes, ids):
            if cls == 0:  # "person" class index is 0
                x1, y1, x2, y2 = map(int, box)
                track_id = int(obj_id.item())

                if x1 <= x <= x2 and y1 <= y <= y2:
                    found_id = int(track_id)
                    break

    if highlighted_id is not None and highlighted_id == found_id:
        highlighted_id = None
    else:
        highlighted_id = found_id

    # Pass highlighted_id argument to gen_frames function
    socketio.emit('frame_update', {'data': 'update frame', 'highlighted_id': highlighted_id})


shooter_on, feeder_on = False, False
@socketio.on('button_click')
def handle_button_click(data):
    global cam_pan, shooter, feeder, shooter_on, feeder_on

    angle_change = 10  # Adjust the value to control the angle change per click

    if data.get('direction') == 'left':
        cam_pan -= angle_change
    elif data.get('direction') == 'right':
        cam_pan += angle_change
    elif data.get('direction') == 'bottom':
        cam_pan = 90
    elif data.get('direction') == 'shooter':
        if shooter_on:
            stopShooter()
            shooter_on = False
        else:
            startShooter(30)
            shooter_on = True
    elif data.get('direction') == 'feeder':
        if feeder_on:
            stopFeeder()
            feeder_on = False
        else:
            startFeeder(100)
            feeder_on = True


    cam_pan = max(0, min(180, cam_pan))  # Ensure the angle is within the valid range
    panAngle(int(cam_pan - 90))



last_sent = 0
update_interval = 1  # Send data every 0.1 seconds


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
    try:
        socketio.run(app, host='192.168.31.177', port=9090, allow_unsafe_werkzeug=True)
    finally:
        robot.motor_stop()
