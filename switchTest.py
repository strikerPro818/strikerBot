import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(17, GPIO.IN)

GPIO.setup(5, GPIO.IN)

GPIO.setup(6, GPIO.IN)
GPIO.setup(5, GPIO.IN) #
GPIO.setup(21, GPIO.IN) # Shooter Input

GPIO.setup(26, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)

shooter = GPIO.PWM(26, 100)
shooter.start(0)

feeder = GPIO.PWM(19, 100)
feeder.start(0)


def set_duty_cycle(distance):
    # Map the distance to a duty cycle
    # duty_cycle = ((distance / 10) + 20)
    duty_cycle = float(distance) / float(320 * 240) * 30000
    # duty_cycle = float(distance) / float(320 * 240) * 90000

    voltage = (duty_cycle / 100) * (10 - 0.3) + 0.3
    # duty =

    shooter.ChangeDutyCycle(duty_cycle)
    return duty_cycle, voltage


while True:
    # feeder.ChangeDutyCycle(0)

    if (GPIO.input(21) == True):
        print("shooter triggered")
        shooter.ChangeDutyCycle(30)
    else:
        shooter.ChangeDutyCycle(0)

    if (GPIO.input(5) == True):
        print("feeder triggered")
        feeder.ChangeDutyCycle(100)
    else:
        feeder.ChangeDutyCycle(0)

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
    # if (GPIO.input(5) == True):
    #     print('triggered')
    #     pwm.ChangeDutyCycle(40)
    # if (True):
    #     print('true')
    #     pwm.ChangeDutyCycle(40)

    # if (GPIO.input(21) == True):
    #     pwm.ChangeDutyCycle(0)

    # else:
    #     pwm.ChangeDutyCycle(30)

    # if (GPIO.input(21) == True):
    #     pwm.ChangeDutyCycle(0)

    # if (GPIO.input(21) == True):
    #     distance = 0
    #
    #     set_duty_cycle(distance)

    time.sleep(0.1)
