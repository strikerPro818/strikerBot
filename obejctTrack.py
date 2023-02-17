import random
import time
import json
from huskylib import HuskyLensLibrary
from gpiozero import AngularServo
import time
from time import sleep
from gpiozero.pins.pigpio import PiGPIOFactory
from gpiozero import Servo
from time import sleep
import pigpio
import os
import math
import pid
import PWMServo
# from pantilthat import *
from piservo import Servo
# servoX_pid1 = pid.PID(P=0.33, I=0.6, D=0.066)#pid初始化 #左右
servoX_pid1 = pid.PID(P=0.01, I=0, D=0)
sevoX_track_zero = 1500
# open_io="sudo pigpiod"
# os.system(open_io)
# time.sleep(1)
#扩展板PWM接口1-8号对应扩展板IO口分别为12,16,20,21,19,13,5,6 。(树莓派扩展板7号和8号舵机接口为5V电压，所以9g舵机建议接PWM7和8号接口）
#如需更改接口请参考上方说明修改IO口号即可。
# pin = 13 #要控制的IO口，这里以扩展板PWM1号接口为例。
PULSE_WIDTH_0 = 500
PULSE_WIDTH_180 = 2500
# pi = pigpio.pi()
# pi.set_PWM_range(pin, 20000)#pin是要输出PWM的IO口， 20000设定PWM的调节范围，
#                           #我们的舵机的控制信号是50Hz，就是20ms为一个周期。就是20000us。
#                           #设为20000,就是最小调节为1us
# pi.set_PWM_frequency(pin, 50) #设定PWM的频率，pin是要设定的IO口， 50 是频率
# pi.set_PWM_dutycycle(pin, 2500)
# pigpio_factory = PiGPIOFactory()
# servo = Servo(18, pin_factory=pigpio_factory)
# servo = AngularServo(13, min_pulse_width=0.0006, max_pulse_width=0.0023)
servo = Servo(13)


from src.rmd_x8 import RMD_X8 
import time 
# Setup a new RMD_X8 motor with its identifier.
robot = RMD_X8(0x141)
robot.setup()

startangle = 0
anglestarted = 0

def panAngle(angle):
    # if 0 == anglestarted:
    #     print("Startangle")
    #     rr = robot.read_multi_turns_angle()
    #     print(rr,"srr")
    #     startangle.from_bytes(rr.DL[1:5])
    #     print("\nStartangle:",startangle)
    #     return
    
    
    target = angle*100*6;
    bb = target.to_bytes(4,'little')
    print("Angle:",angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.2)    
# servo.write(180)
# servoX_pid1.SetPoint = 0
# servoX_pid1.update(1)
def pan(angleValue):
#     if angleValue>0:
    panAngle(angleValue)
    #servo.write(angleValue)
#     else:
#         servo.write(-angleValue)
    print('AngleV:',angleValue)
#     microSeconds = PULSE_WIDTH_0 + (angleValue / 180) * (PULSE_WIDTH_180 - PULSE_WIDTH_0)
#     microSeconds = map(angleValue, 0, 180, 500, 2500)
#     servo.servoWrite(Math.round(microSeconds))
#     servoX_pid1.output = round(microSeconds)
#     print('micro',round(microSeconds))#
#     pi.set_PWM_dutycycle(pin, 2500)
#     servo.angle = angleValue
#     servo.angle = angleValue
#     sleep(0.01)
#     servo.angle = angleValue
#     sleep(0.3)
#     sleep(1


# pan(0)
FRAME_W = 320
FRAME_H = 240
cam_pan = 90

hl = HuskyLensLibrary("I2C","", address=0x32)

def printObjectNicely(obj):
    count=1
    if(type(obj)==list):
        for i in obj:
            print("\t "+ ("BLOCK_" if i.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(i.__dict__))
            count+=1
    else:
        print("\t "+ ("BLOCK_" if obj.type=="BLOCK" else "ARROW_")+str(count)+" : "+ json.dumps(obj.__dict__))
        
# hl.algorthim("ALGORITHM_OBJECT_TRACKING")
# currentX = hl.blocks().learned

#         tilt(int(cam_tilt-90))
    
# while(hl.learnedObjCount()>0):
while(True):
    try:
    
        x = hl.blocks().x
        
        w = hl.blocks().width
        if(hl.learnedObjCount()>0):
            print('currentX', x)
            x = x + (w/2)
#     y = y + (h/2)

        # Correct relative to center of image
            turn_x  = float(x - (FRAME_W/2))
#     turn_y  = float(y - (FRAME_H/2))

        # Convert to percentage offset
            turn_x  /= float(FRAME_W/2)
#         turn_y  /= float(FRAME_H/2)

        # Scale offset to degrees
            turn_x   *= 3 # VFOV
#         turn_y   *= 1.3 # HFOV
            cam_pan  += -turn_x
#         cam_tilt += turn_y
            
            print('move',cam_pan-90)

        # Clamp Pan/Tilt to 0 to 180 degrees
            cam_pan = max(0,min(180,cam_pan))
#         cam_tilt = max(0,min(180,cam_tilt))
#         print(
        # Update the servos
            pan(int(cam_pan))
#             print('exe')
            
#             sleep(0.3)
#             pan(int(cam_pan-90))
    except:continue
        
# while(True):
#     try:
#         if(hl.count()>0):
#             print(hl.blocks().x)
#     except:
#         continue
        
    
        
        
# while(hl.learnedObjCount()>0):
#     if(hl.learnedObjCount()>0):
#         printObjectNicely(hl.blocks())
#     else:
#         pass