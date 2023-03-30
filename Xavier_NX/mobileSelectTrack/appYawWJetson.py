from flask import Flask, Response
import jetson_inference as ji
import jetson_utils as ju
import cv2
from flask import Flask, render_template, Response
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config
from flask_socketio import SocketIO, emit
from src.rmd_x8 import RMD_X8
import time
import numpy as np
font = ju.cudaFont()

robot = RMD_X8(0x141)
robot.setup()
cam_size = 640
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 5

# Initialize the detection network and camera
# net = ji.detectNet("ped-100", threshold=0.4,argv=['--overlay=box'])
net = ji.detectNet("ped-100", threshold=0.6)
camera = ju.videoSource("/dev/video1")
# camera = ju.videoSource("v4l2:///dev/video4")

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')
use_cuda = True
tracker = build_tracker(cfg, use_cuda)

highlighted_id = None
app = Flask(__name__)
socketio = SocketIO(app)

def panAngle(angle):
    target = int(angle * 100 * 6)
    bb = target.to_bytes(4, 'little', signed=True)
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.01)

# def draw_boxes(img, detections):
#     for detection in detections:
#         if detection.ClassID == 1:
#             left = int(detection.Left)
#             top = int(detection.Top)
#             right = int(detection.Right)
#             bottom = int(detection.Bottom)
#             ju.cudaDrawRect(img, (left, top, right, bottom), (0, 255, 0, 255))

def draw_boxes_deepSort():
    global tracker, highlighted_id
    while True:
        # Capture a frame from the camera
        img = camera.Capture()

        # Perform object detection on the frame
        detections = net.Detect(img)
        if detections:
            # Convert the detections to the format expected by the tracker
            dets = []
            confidences = []
            clss = []
            for detection in detections:
                left = int(detection.Left)
                top = int(detection.Top)
                right = int(detection.Right)
                bottom = int(detection.Bottom)
                print('Ped Coordinates:',left, top, right, bottom)


                confidence = detection.Confidence
                class_id = detection.ClassID
                dets.append([left, top, right-left, bottom-top])
                confidences.append(confidence)
                clss.append(class_id)
                # font.OverlayText(img,img.width,img.height,'fuck',5,5,font.Blue)


            # Convert the cudaImage object to a numpy array
            img_np_deep = ju.cudaToNumpy(img)

            # Convert the image to BGR colorspace for use with OpenCV
            img_np_deep = cv2.cvtColor(img_np_deep, cv2.COLOR_RGB2BGR)

            # Pass the detections to the tracker to assign IDs

            try:
                tracks = tracker.update(np.array(dets), np.array(confidences), np.array(clss), img_np_deep)
                print(tracks)
            except ValueError or IndexError:
                print('Lost!')
                continue
            for track in tracks:
                # print(track,'Running')
                # if len(track) != 5:
                #     continue
                #     print('continue')
                # print('passed')
                leftD, topD, rightD, bottomD, _, track_id = track
                print('DeepSort Coordinates:',leftD, topD, rightD, bottomD)
                width, height = topD-topD, bottomD-rightD

                # print(left, top, width, height, track_id,'Good Point')
                # if track_id == highlighted_id:
                if highlighted_id is not None and int(track_id) == highlighted_id:
                    color = font.Yellow  # RGBA color for highlighted track (yellow)
                else:
                    color = font.Cyan  # RGBA color for unhighlighted track (green)

                # Add the following lines to display the text within the bounding box:
                text = f"ID: {track_id}"
                text_x = left + 5
                text_y = top + 20
                font.OverlayText(img,img.width,img.height, text,text_x, text_y,color)  # RGBA color for white text

                # ju.cudaDrawRect(img, (left+30, top+30, right+30, bottom+30), color,  font.Gray40)

                # img_np = ju.cudaToNumpy(img)
                #
                # # Convert the image to BGR colorspace for use with OpenCV
                # img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
                # cv2.rectangle(img_np, (left, y1), (x2, y2), color, 2)
                # cv2.putText(img_np, str(track_id), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                # ju.cudaDrawRect(img, (left+100, top, width, height), color,  font.Gray40)
                # # font.OverlayText(img, left, top, f"ID:{track_id}")
                # # ju.cudaDrawRect(img, (center_x - sight_width // 2, center_y - sight_thickness // 2,
                # #                 center_x + sight_thickness // 2, center_y + sight_width // 2), color,font.Gray40)
                # # ju.cudaDeviceSynchronize()
                # font.OverlayText(img, 500, 500, f"ID:{track_id}")
            # print('check ran')
            # Store the ID of the highlighted track (if any) for use in other functions
            # if len(tracks) == 1:
            #     highlighted_id = tracks[0][4]
            # else:
            #     highlighted_id = None
        # print('img here')

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
# def generate_frames():
#     global cap, model, tracker, highlighted_id, outputs, cam_pan  # Add cam_pan to the global variables
#     while True:
#         # Capture a frame from the camera
#         img = camera.Capture()
#
#         # Perform object detection on the frame
#         detections = net.Detect(img)
#
#         # Draw boxes around the detected objects
#         # draw_boxes(img, detections)
#         draw_boxes_deepSort(img, detections)
#
#
#
#         # Convert the cudaImage object to a numpy array
#         img_np = ju.cudaToNumpy(img)
#
#         # Convert the image to BGR colorspace for use with OpenCV
#         img_np = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
#
#         # Perform some processing on the numpy array here...
#         # For example, you could apply a filter or resize the image.
#
#         # Convert the numpy array back to a JPEG byte stream
#         ret, buffer = cv2.imencode('.jpg', img_np)
#         frame = buffer.tobytes()
#
#         # Yield the frame as a Flask response
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')






outputs = []


@socketio.on('click_event')
def handle_click_event(data):
    global highlighted_id, outputs
    x, y = data['x'], data['y']

    found_id = None
    for output in outputs:
        left, top, width, height, _, track_id = output
        if left <= x <= top and width <= y <= height:
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

# @app.route('/video_feed')
# def video_feed():
#     # return Response(generate_frames(), content_type='multipart/x-mixed-replace; boundary=frame')
#     return Response(draw_boxes_deepSort(), content_type='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_feed')
def video_feed():
    return Response(draw_boxes_deepSort(), content_type='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    socketio.run(app, host='192.168.31.177', port=9090, allow_unsafe_werkzeug=True)
    # app.run(host='192.168.31.177', port=9090, debug=True)

# Release resources
camera.Close()
