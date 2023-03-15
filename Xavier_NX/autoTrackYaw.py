import torch
import cv2
from src.rmd_x8 import RMD_X8
import time
import os
import torch.hub

robot = RMD_X8(0x141)
robot.setup()
cam_size = 1600
FRAME_W = cam_size
FRAME_H = cam_size
cam_pan = 90
angleVector = 15

# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
# model = torch.hub.load('ultralytics/yolov5', 'custom', path_or_model='yolov5s.pt', force_reload=False)
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/', model='yolov5s', source='local')

model.cuda()
model.conf = 0.38
# model.iou = 0.45

# cap = cv2.VideoCapture(0)
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, cam_size)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, cam_size)

# Create a CUDA GpuMat object for the grayscale image
gray_gpu = cv2.cuda_GpuMat()

def panAngle(angle):
    # angle = max(-90, min(90, angle))
    target = int(angle * 100 * 6);
    bb = target.to_bytes(4, 'little', signed=True)
    print()
    print("Executed Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.01)

# bg_image = cv2.imread('c1.png', cv2.IMREAD_UNCHANGED)
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    frame_height, frame_width = frame.shape[:2]

    # Convert the input frame to a CUDA GpuMat
    frame_gpu = cv2.cuda_GpuMat()
    frame_gpu.upload(frame)

    # Convert the image to grayscale on the GPU
    if frame_gpu.channels() == 3:
        gray_gpu = cv2.cuda.cvtColor(frame_gpu, cv2.COLOR_BGR2GRAY)
    else:
        gray_gpu = frame_gpu

    # Download the grayscale image from the GPU
    gray = gray_gpu.download()

    # Detect humans using YOLOv5
    results = model(frame, size=640)

    # Get the coordinates of the detected humans
    boxes = results.xyxy[0].cpu().numpy()

    # Draw a red scope to divide the frame into four sections
    scope_thickness = 2
    scope_color = (0, 0, 255)
    cv2.line(frame, (0, frame_height // 2), (frame_width, frame_height // 2), scope_color, scope_thickness)
    cv2.line(frame, (frame_width // 2, 0), (frame_width // 2, frame_height), scope_color, scope_thickness)

    # Draw bounding boxes around the detected humans and show the x, y, height and width
    for box in boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            center_x, center_y = x + w // 2, y + h // 2
            cv2.putText(frame, f'x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0),
                        2)

            # Draw a realistic sight scope at the center of the bounding box
            sight_width = int(w * 0.2)
            sight_thickness = int(w * 0.005)
            sight_color = (0, 255, 0)

            # Draw the sight scope
            cv2.rectangle(frame, (center_x - sight_width // 2, center_y - sight_thickness // 2),
                          (center_x + sight_width // 2, center_y + sight_thickness // 2), sight_color, -1)
            cv2.rectangle(frame, (center_x - sight_thickness // 2, center_y - sight_width // 2),
                          (center_x + sight_thickness // 2, center_y + sight_width // 2), sight_color, -1)
            cv2.circle(frame, (center_x, center_y), sight_width // 2, sight_color, sight_thickness)

            # Draw a line from the center of the bounding box to the center of the frame
            cv2.line(frame, (center_x, center_y), (frame_width // 2, frame_height // 2), (0, 255, 0), 2)

            # Move the camera to center the bounding box
            print(f"x: {x1}, y: {y1}, width: {x2 - x1}, height: {y2 - y1}")

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

        # Display the resulting frame
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        robot.motor_stop()
        break
cap.release()
cv2.destroyAllWindows()
robot.motor_stop()

