import smbus2
import struct
import time

# Set the I2C slave address of QMI8658C
qmi_address = 0x6B

# Set the register addresses of pitch angle in QMI8658C
pitch_reg = 0x3D
pitch_high_reg = 0x3D
pitch_low_reg = 0x3E

# Set the sensitivity of the pitch angle change detection
sensitivity = 0.1

# Set the initial pitch angle value
prev_pitch = None

# Set the final pitch angle value
final_pitch = None

# Create an SMBus object for I2C communication
bus = smbus2.SMBus(1)

# Wait for the user to press the 'Enter' key to start recording the pitch angle
input('Press Enter to start recording...')

# Record the initial pitch angle
pitch_high_byte = bus.read_byte_data(qmi_address, pitch_high_reg)
pitch_low_byte = bus.read_byte_data(qmi_address, pitch_low_reg)
pitch_bytes = bytes([pitch_high_byte, pitch_low_byte])
prev_pitch = struct.unpack('>h', pitch_bytes)[0] * 0.061

# Wait for some time before checking the pitch angle again
time.sleep(0.1)

while True:
    # Read the pitch angle from QMI8658C
    pitch_high_byte = bus.read_byte_data(qmi_address, pitch_high_reg)
    pitch_low_byte = bus.read_byte_data(qmi_address, pitch_low_reg)
    pitch_bytes = bytes([pitch_high_byte, pitch_low_byte])
    pitch = struct.unpack('>h', pitch_bytes)[0]

    # Convert the pitch angle to degrees
    pitch_deg = pitch * 0.000061

    # pitch_deg = pitch * 0.0000061


    # Check if the pitch angle has changed by more than the sensitivity threshold
    if abs(pitch_deg - prev_pitch) >= sensitivity:
        print('Pitch angle changed: {:.2f} degrees'.format(pitch_deg))
        prev_pitch = pitch_deg

    # Check if the user has pressed the 'q' key to record the final pitch angle
    if input('Press q to record final pitch angle: ') == 'q' and final_pitch is None:
        final_pitch = pitch_deg
        print('Final pitch angle: {:.2f} degrees'.format(final_pitch))

    # Wait for some time before checking again
    time.sleep(0.1)

    # If the final pitch angle has been recorded, exit the loop and end the program
    if final_pitch is not None:
        break
