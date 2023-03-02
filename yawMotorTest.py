from src.rmd_x8 import RMD_X8
import time
import os
import huskylib
from huskylib import HuskyLensLibrary
import numpy as np

os.system('sudo ip link set can0 up type can bitrate 1000000')
os.system('sudo ifconfig can0 txqueuelen 65536')

robot = RMD_X8(0x141)
robot.setup()

FRAME_W = 320
FRAME_H = 240
cam_pan = 90
alpha = 0.2  # low-pass filter coefficient

hl = HuskyLensLibrary("I2C", "", address=0x32)


def panAngle(angle):
    # angle = max(-90, min(90, angle))
    target = int(angle * 100 * 6);
    bb = target.to_bytes(4,'little',signed=True)
    print()
    print("EXE Angle:", angle)
    robot.position_closed_loop_1(bb)
    # time.sleep(1)
    # robot.motor_stop()

def predict_x(x, w, prev_x, prev_w, dt):
    # Simple linear prediction model
    dx = x - prev_x
    dw = w - prev_w
    x_pred = x + dx/dt
    w_pred = w + dw/dt
    return x_pred, w_pred

panAngle(0)

prev_x = 0
prev_w = 0
prev_time = time.time()

while True:
    try:
        x = hl.blocks().x
        w = hl.blocks().width

        if hl.learnedObjCount() > 0:
            x, w = predict_x(x, w, prev_x, prev_w, time.time()-prev_time)
            prev_x = x
            prev_w = w
            prev_time = time.time()
            print(x, w)
            x = x + (w / 2)
            turn_x = float(x - (FRAME_W / 2))
            turn_x /= float(FRAME_W / 2)
            turn_x *= 1.2  # VFOV
            cam_pan += -turn_x
            print('Move: ', cam_pan - 90)
            cam_pan = max(0, min(180, cam_pan))
            panAngle(int(cam_pan - 90))
        else:
            robot.motor_stop()

    except Exception as e:
        print(e)
        continue