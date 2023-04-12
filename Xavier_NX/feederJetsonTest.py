import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)

feeder = GPIO.PWM(33, 100)
feeder.start(0)
speed = 0
while True:
    feeder.ChangeDutyCycle(speed)
    print('Duty cycle:',speed)
    # print("Current duty cycle: {:.2f}".format(duty_cycle))
    time.sleep(0.1)
# pwm.ChangeDutyCycle(0)
shooter.Stop()
GPIO.cleanup()