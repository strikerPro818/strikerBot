from src.rmd_x8 import RMD_X8
import time
# Setup a new RMD_X8 motor with its identifier.
robot = RMD_X8(0x141)
robot.setup()

angle=0
target = angle*100*6;
bb = target.to_bytes(4,'little',signed=True)
robot.position_closed_loop_1(bb)

time.sleep(1)

robot.motor_stop()