import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(17, GPIO.IN)

GPIO.setup(13, GPIO.IN)
GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.IN)
GPIO.setup(21, GPIO.IN)

GPIO.setup(26, GPIO.OUT)

pwm = GPIO.PWM(26, 100)
pwm.start(0)

def set_duty_cycle(distance):
    # Map the distance to a duty cycle
    # duty_cycle = ((distance / 10) + 20)
    duty_cycle = float(distance) / float(320 * 240) * 30000
    # duty_cycle = float(distance) / float(320 * 240) * 90000

    voltage = (duty_cycle / 100) * (10 - 0.3) + 0.3
    # duty =

    pwm.ChangeDutyCycle(duty_cycle)
    return duty_cycle,voltage

while True:
    # if (GPIO.input(17) == True):
    #     print("Object Detected!")
    # else:
    #     # pwm.ChangeDutyCycle(30)
    #     print("Not Dectected!")
    # if (GPIO.input(13) == True):
    #     pass
    #     # hl.learn()
    #
    # if (GPIO.input(6) == True):
    #     pass
    #     # hl.forget()
    if (GPIO.input(5) == True):
        pwm.ChangeDutyCycle(30)

    if (GPIO.input(21) == True):
        pwm.ChangeDutyCycle(0)

    # else:
    #     pwm.ChangeDutyCycle(30)

    # if (GPIO.input(21) == True):
    #     pwm.ChangeDutyCycle(0)

    # if (GPIO.input(21) == True):
    #     distance = 0
    #
    #     set_duty_cycle(distance)

    time.sleep(0.1)