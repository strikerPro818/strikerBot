import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(26, GPIO.OUT)
shooter = GPIO.PWM(26, 100)
shooter.start(0)

feeder = GPIO.setup(19, GPIO.OUT)
feeder = GPIO.PWM(19, 50)
feeder.start(0)
feederInput = GPIO.setup(13, GPIO.IN)

print('test')


# shooter.ChangeDutyCycle(30)
def voltage_to_duty_cycle(Vout):
    return (Vout - 0.4) / (4.8 - 0.4) * 100


# Map duty cycle range (0% - 100%) to output voltage range (0.4V - 4.8V)
def duty_cycle_to_voltage(D):
    return (D / 100) * (4.8 - 0.4) + 0.4


# Vout = duty_cycle_to_voltage(D)
# print(Vout)

try:
    while True:
        # pass
        # feeder.ChangeDutyCycle(0)



    # relativeDuty = 30
    # convertedDuty = relativeDuty * 0.45
    # print(convertedDuty)
    # while True:
        # shooter.ChangeDutyCycle(convertedDuty)
        # feeder.ChangeDutyCycle()
        shooter.ChangeDutyCycle(0)
        #
        # # feeder.ChangeDutyCycle(0)
        # time.sleep(0.1)



except KeyboardInterrupt:

    # Clean up GPIO pins on keyboard interrupt
    feeder.stop()
    shooter.stop()
    GPIO.cleanup()
    # GPIO.output(20, GPIO.HIGH)
    # print('feed')

    # GPIO.output(21, GPIO.HIGH)
#     print(15*0.3)
#     feeder.ChangeDutyCycle(23)
#     GPIO.output(11, GPIO.HIGH)

# shooter.ChangeDutyCycle(30)

# shooter.ChangeDutyCycle(30)
# feeder.ChangeDutyCycle(100)

# feeder.ChangeDutyCycle(0)

# shooter.ChangeDutyCycle(30)
