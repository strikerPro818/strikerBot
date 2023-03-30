from flask import Flask, render_template
from flask_socketio import SocketIO
from ultralytics import YOLO
import cv2
import base64

app = Flask(__name__)
socketio = SocketIO(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def test_connect():
    print('Client connected')

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected')

@socketio.on('start_stream')
def start_stream():
    # Load the YOLO model
    model = YOLO("/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov8n.engine", task='detect')
    results = model.track(source=1, show=False, stream=True, tracker="botsort.yaml")

    # Loop through the results and send each frame to the client
    for result in results:
        img = result.orig_img
        if result.boxes is not None:
            boxes = result.boxes.xyxy.to("cpu").numpy()
            classes = result.boxes.cls.to("cpu").numpy()
            if result.boxes.id is not None:
                ids = result.boxes.id.numpy()
                for box, cls, obj_id in zip(boxes, classes, ids):
                    if cls == 0:  # "person" class index is 0
                        x1, y1, x2, y2 = map(int, box)
                        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)  # Draw a green rectangle around the person
                        cv2.putText(img, f"ID: {int(obj_id.item())}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    (0, 255, 0), 2)

        # Encode the frame as base64 and send it to the client
        _, buffer = cv2.imencode('.jpg', img)
        frame = base64.b64encode(buffer).decode('utf-8')
        socketio.emit('frame', frame)

if __name__ == '__main__':
    socketio.run(app, host='192.168.31.177', port=9090, debug=True,allow_unsafe_werkzeug=True)
