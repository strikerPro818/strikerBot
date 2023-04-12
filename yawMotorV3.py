import time

from src.rmd_x8 import RMD_X8
# print('hi')
robot = RMD_X8(0x141)
robot.setup()

angle = 45  # Change this value to the desired angle
target = angle * 100
desired_speed = 8000

# Convert target angle and maximum speed to bytes
angle_bytes = target.to_bytes(4, 'little', signed=True)
speed_bytes = desired_speed.to_bytes(2, 'little', signed=True)

# Prepare the data list
data = list(speed_bytes) + list(angle_bytes)

# Print the values for debugging
print(f"Target Angle: {angle}")
print(f"Target Value: {target}")
print(f"Angle Bytes: {list(angle_bytes)}")
print(f"Speed Bytes: {list(speed_bytes)}")
print(f"Data List: {data}")

# Call the new method with the updated data
robot.position_closed_loop_2(data)
time.sleep(1)

robot.motor_stop()


