import cv2
# import torch
from src.rmd_x8 import RMD_X8
import time
import os
# import torch
import torch

robot = RMD_X8(0x141)
robot.setup()
cam_size = 1600
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 10

# model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/', model='yolov5s', source='local')
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/',model='yolov5s',source='local')

model.cuda()
# model.conf = 0.43

cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_size)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_size)

gray_gpu = cv2.cuda_GpuMat()

# Load the PNG overlay image
overlay_img = cv2.imread("/home/striker/Jetson/Xavier_NX/c2.png")

def panAngle(angle):
    # angle = max(-90, min(90, angle))
    target = int(angle * 100 * 6);
    bb = target.to_bytes(4, 'little', signed=True)
    print()
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.01)
# panAngle(0)

while True:
    ret, frame = cap.read()


    frame_height, frame_width = frame.shape[:2]

    frame_gpu = cv2.cuda_GpuMat()
    frame_gpu.upload(frame)

    if frame_gpu.channels() == 3:
        gray_gpu = cv2.cuda.cvtColor(frame_gpu, cv2.COLOR_BGR2GRAY)
    else:
        gray_gpu = frame_gpu

    gray = gray_gpu.download()

    results = model(frame,size=640)
    # results = model(frame)

    boxes = results.xyxy[0].cpu().numpy()

    scope_thickness = 2
    scope_color = (0, 0, 255)
    cv2.line(frame, (0, frame_height // 2), (frame_width, frame_height // 2), scope_color, scope_thickness)
    cv2.line(frame, (frame_width // 2, 0), (frame_width // 2, frame_height), scope_color, scope_thickness)

    for box in boxes:
        if box[5] == 0:
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            center_x, center_y = x + w // 2, y + h // 2
            cv2.putText(frame, f'x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        2)

            sight_width = int(w * 0.2)
            sight_thickness = int(w * 0.005)
            sight_color = (0, 255, 0)

            cv2.rectangle(frame, (center_x - sight_width // 2, center_y - sight_thickness // 2),
            (center_x + sight_thickness // 2, center_y + sight_width // 2), sight_color, -1)
            cv2.circle(frame, (center_x, center_y), sight_width // 2, sight_color, sight_thickness)
            cv2.line(frame, (center_x, center_y), (frame_width // 2, frame_height // 2), (0, 255, 0), 2)


            overlay_resized = cv2.resize(overlay_img, (frame.shape[1], frame.shape[0]))
            alpha = 0.30  # Set the alpha value to control the opacity of the overlay

            blended = cv2.addWeighted(frame, 1 - alpha, overlay_resized, alpha, 0,
                                      frame)  # Add overlay to original frame


            frame_height, frame_width = frame.shape[:2]

            trackX = x1
            trackW = x2 - x1
            trackX = trackX + (trackW / 2)
            turn_x = float(trackX - (FRAME_W / 2))
            turn_x /= float(FRAME_W / 2)
            turn_x *= angleVector
            cam_pan += -turn_x
            cam_pan = max(0, min(180, cam_pan))
            panAngle(int(cam_pan - 90))

    # cv2.imshow('frame', frame)

    cv2.imshow("Overlay", blended)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        robot.motor_stop()
        break

cap.release()
cv2.destroyAllWindows()
robot.motor_stop()

