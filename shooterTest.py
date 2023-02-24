import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(26, GPIO.OUT)
shooter = GPIO.PWM(26, 100)
shooter.start(0)

GPIO.setup(19, GPIO.OUT)
feeder = GPIO.PWM(19, 100)
feeder.start(0)
# feederInput = GPIO.setup(19, GPIO.IN)

print('test')
# shooter.ChangeDutyCycle(30)

while True:
    shooter.ChangeDutyCycle(0)
    # feeder.ChangeDutyCycle(100)

    # feeder.ChangeDutyCycle(0)

    # shooter.ChangeDutyCycle(30)

