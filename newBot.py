from src.rmd_x8 import RMD_X8
import time
import json
from huskylib import HuskyLensLibrary
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(26, GPIO.OUT)
shooter = GPIO.PWM(26, 100)
shooter.start(0)

GPIO.setup(19, GPIO.OUT)
feeder = GPIO.PWM(19, 100)
feeder.start(0)

# sudo ip link set can0 up type can bitrate 1000000
# sudo ifconfig can0 txqueuelen 65536

# Setup a new RMD_X8 motor with its identifier.
robot = RMD_X8(0x141)
robot.setup()

startangle = 0
anglestarted = 0

FRAME_W = 320
FRAME_H = 240
cam_pan = 90

hl = HuskyLensLibrary("I2C", "", address=0x32)
def printObjectNicely(obj):
    count = 1
    if (type(obj) == list):
        for i in obj:
            print("\t " + ("BLOCK_" if i.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(i.__dict__))
            count += 1
    else:
        print("\t " + ("BLOCK_" if obj.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(obj.__dict__))



def panAngle(angle):
    target = angle * 100 * 6;
    bb = target.to_bytes(4, 'little')
    print("Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.2)


def pan(angleValue):
    panAngle(angleValue)
    print('Angle Executed:', angleValue)







while (True):
    try:

        x = hl.blocks().x

        w = hl.blocks().width
        if hl.learnedObjCount() > 0:
            print('currentX', x)
            x = x + (w / 2)
            #     y = y + (h/2)

            # Correct relative to center of image
            turn_x = float(x - (FRAME_W / 2))
            #     turn_y  = float(y - (FRAME_H/2))

            # Convert to percentage offset
            turn_x /= float(FRAME_W / 2)
            #         turn_y  /= float(FRAME_H/2)

            # Scale offset to degrees
            turn_x *= 3  # VFOV
            #         turn_y   *= 1.3 # HFOV
            cam_pan += -turn_x
            #         cam_tilt += turn_y

            print('move', cam_pan - 90)

            # Clamp Pan/Tilt to 0 to 180 degrees
            cam_pan = max(0, min(180, cam_pan))

            pan(int(cam_pan))

    except:
        continue
