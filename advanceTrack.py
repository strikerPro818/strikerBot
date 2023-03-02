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

hl = HuskyLensLibrary("I2C", "", address=0x32)


def panAngle(angle):
    # angle = max(-90, min(90, angle))
    target = int(angle * 100 * 6)
    bb = target.to_bytes(4, 'little', signed=True)
    print()
    print("EXE Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(1)
    robot.motor_stop()


# Set up Kalman filter
dt = 1.0  # Time step
F = np.array([[1, dt], [0, 1]])  # State transition matrix
H = np.array([[1, 0]])  # Observation matrix
Q = np.array([[1, 0], [0, 1]])  # Process noise covariance
R = np.array([[10]])  # Measurement noise covariance
x = np.array([[0], [0]])  # Initial state estimate
P = np.array([[100, 0], [0, 100]])  # Initial state covariance



def kalman_filter(x, P, F, Q, R, z):
    x = np.dot(F, x)
    P = np.dot(F, np.dot(P, F.T)) + Q

    # measurement update
    y = z - np.dot(H, x)
    S = R + np.dot(H, np.dot(P, H.T))
    K = np.dot(P, np.dot(H.T, np.linalg.inv(S)))
    x += np.dot(K, y)
    P = np.dot((np.eye(4) - np.dot(K, H)), P)

    return x, P


panAngle(0)

# Initialize Kalman filter with initial position estimate
z = 90
cam_pan = kalman_filter(z)

while True:
    try:
        x = hl.blocks().x
        w = hl.blocks().width

        if (hl.learnedObjCount() > 0):
            # Use Kalman filter to smooth out pan movement
            x = x + (w / 2)
            z = x / FRAME_W * 180  # Convert x position to degrees
            cam_pan = kalman_filter(z)

            # Send pan angle to motor
            print('Move:', cam_pan - 90)
            cam_pan = max(0, min(180, cam_pan))
            panAngle(int(cam_pan - 90))

        else:
            robot.motor_stop()
    except:
        continue
