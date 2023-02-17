

from src.rmd_x8 import RMD_X8 
import time 
# Setup a new RMD_X8 motor with its identifier.
robot = RMD_X8(0x141)
robot.setup()

startangle = 0
anglestarted = 0

def panAngle(angle):
    target = angle*100*6;
    bb =target.to_bytes(4,'little')
    print("Angle:",angle)
    robot.position_closed_loop_1(bb)
    time.sleep(0.2)
    

ta = 0
while True:
    #ta += 0.1
    panAngle(0)
    time.sleep(0.1)
    break