from src.rmd_x8 import RMD_X8 
import time
from huskylib import HuskyLensLibrary

# Setup a new RMD_X8 motor with its identifier.

# sudo ip link set can0 up type can bitrate 1000000
# sudo ifconfig can0 txqueuelen 65536
robot = RMD_X8(0x141)
robot.setup()

FRAME_W = 320
FRAME_H = 240
cam_pan = 90

hl = HuskyLensLibrary("I2C","", address=0x32)

# angle=0
# target = angle*100*6;
# bb = target.to_bytes(4,'little')
# robot.position_closed_loop_1(bb)
def printObjectNicely(obj):
    count=1
    if(type(obj)==list):
        for i in obj:
            print("\t "+ ("BLOCK_" if i.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(i.__dict__))
            count+=1
    else:
        print("\t "+ ("BLOCK_" if obj.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(obj.__dict__))

def panAngle(angle):
    target = angle * 100 * 6;
    bb = target.to_bytes(4,'little',signed=True)
    print("Angle:", angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.1)
    robot.motor_stop()
    # time.sleep(0.2)

def pan(angleValue):
    panAngle(angleValue)
    print('AngleV:',angleValue)

# def shootDistance()

# def getAxis():
#     x = hl.blocks().x
#     w = hl.blocks().width
#     return x,w

while(True):
    try:
        x = hl.blocks().x
        w = hl.blocks().width
        # robot.motor_stop()

        if (hl.learnedObjCount() > 0):
            print(x,w)
            x = x + (w/2)
            turn_x = float(x - (FRAME_W / 2))
            turn_x  /= float(FRAME_W/2)
            turn_x   *= 5.0 # VFOV
            cam_pan  += -turn_x
            print('Move: ',cam_pan-90)
            cam_pan = max(0,min(180,cam_pan))
            # print('cam_pan',cam_pan)
            pan(int(cam_pan-90))
        else:
            robot.motor_stop()


    except:
        None


# robot.motor_stop()