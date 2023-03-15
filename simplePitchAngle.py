import smbus
import time
import math

# I2C address of the QMI8658 IMU
I2C_ADD_IMU_QMI8658 = 0x6b

# Register addresses for the accelerometer and gyroscope readings
QMI8658Register_Ax_L = 0x28

# Create an instance of the smbus module for I2C communication
bus = smbus.SMBus(1)

# Function to read a block of data from the IMU
def read_block(addr, reg, length):
    return bus.read_i2c_block_data(addr, reg, length)

# Initialize the gyro offset values (if needed)
GyroOffset = [0, 0, 0]

# Loop to continuously read and print the gyro and accelerometer data
while True:
    # Read the gyro and accelerometer data from the IMU
    data = read_block(I2C_ADD_IMU_QMI8658, QMI8658Register_Ax_L, 12)

    # Parse the raw data into gyro and accelerometer values
    Accel = [0, 0, 0]
    Gyro = [0, 0, 0]
    Accel[0] = (data[1] << 8) | data[0]
    Accel[1] = (data[3] << 8) | data[2]
    Accel[2] = (data[5] << 8) | data[4]
    Gyro[0] = ((data[7] << 8) | data[6]) - GyroOffset[0]
    Gyro[1] = ((data[9] << 8) | data[8]) - GyroOffset[1]
    Gyro[2] = ((data[11] << 8) | data[10]) - GyroOffset[2]

    # Convert the gyro and accelerometer values to physical units (if needed)
    Accel = [a/16384.0 for a in Accel]
    Gyro = [g*0.0175 for g in Gyro]
    pitch = math.atan2(Accel[0], math.sqrt(Accel[1]**2 + Accel[2]**2)) * 180 / math.pi

    # Print the gyro and accelerometer values to the console
    print("Accel: {}, Gyro: {}, Pitch: {}".format(Accel, Gyro,pitch))
    time.sleep(1)
