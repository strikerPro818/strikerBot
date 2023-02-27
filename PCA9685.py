# # from __future__ import division    # python2使用
# import time
# import Adafruit_PCA9685             # 调用PCA9685模块
#
# pwm = Adafruit_PCA9685.PCA9685()
# # 设置最大最小脉冲长度
# servo_min =  90  # 4096的最小脉冲长度
# servo_max = 640  # 4096的最大脉冲长度
# servo_mid = 365  # 4096的中间脉冲长度
# # 设置频率为60
# pwm.set_pwm_freq(60)
# print('Moving servo on, press Ctrl-C to quit...')
# while True:
#     # pwm.set_pwm(0, 0 , )
#     pwm.set_pwm(0, 0, servo_min)
#     time.sleep(1)
#     pwm.set_pwm(0, 0, servo_max)
#     time.sleep(1)
# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# This simple test outputs a 50% duty cycle PWM single on the 0th channel. Connect an LED and
# resistor in series to the pin to visualize duty cycle changes and its impact on brightness.

from board import SCL, SDA
import busio

# Import the PCA9685 module.
from adafruit_pca9685 import PCA9685

# Create the I2C bus interface.
i2c_bus = busio.I2C(SCL, SDA)

# Create a simple PCA9685 class instance.
pca = PCA9685(i2c_bus)

# Set the PWM frequency to 60hz.
pca.frequency = 60

# Set the PWM duty cycle for channel zero to 50%. duty_cycle is 16 bits to match other PWM objects
# but the PCA9685 will only actually give 12 bits of resolution.
pca.channels[0].duty_cycle = 0x7FFF