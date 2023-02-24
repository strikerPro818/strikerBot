from src.rmd_x8 import RMD_X8
import time

# sudo ip link set can0 up type can bitrate 1000000
# sudo ifconfig can0 txqueuelen 65536

robot = RMD_X8(0x141)
robot.setup()


def panAngle(angleInput):
    angle = angleInput
    target = angle * 100 * 6;
    bb = target.to_bytes(4, 'little', signed=True)
    robot.position_closed_loop_1(bb)

    time.sleep(1)

    robot.motor_stop()


panAngle(0)
