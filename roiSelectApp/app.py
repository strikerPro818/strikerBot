import cv2
import numpy as np
from flask import Flask, Response, render_template

app = Flask(__name__)
roi = None
tracker = None
cascade = cv2.CascadeClassifier('haarcascade_fullbody.xml')

def select_roi(event, x, y, flags, param):
    global roi, tracker
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = (x, y)
        tracker = cv2.TrackerCSRT_create()
    elif event == cv2.EVENT_LBUTTONUP:
        x0, y0 = roi
        w = x - x0
        h = y - y0
        roi = (x0, y0, w, h)
        tracker.init(frame, roi)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

def gen_frames():
    cap = cv2.VideoCapture(0)
    cv2.namedWindow('Frame')
    cv2.setMouseCallback('Frame', select_roi)
    while True:
        success, frame = cap.read()
        if not success:
            break
        if tracker is not None:
            success, bbox = tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            else:
                tracker = None
        elif roi is not None:
            x, y, w, h = roi
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rects = cascade.detectMultiScale(gray, 1.3, 5)
            if len(rects) > 0:
                x, y, w, h = rects[0]
                roi = (x, y, w, h)
                tracker = cv2.TrackerCSRT_create()
                tracker.init(frame, roi)
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

if __name__ == '__main__':
    app.run(host='192.168.31.190', port=9090, debug=True)

