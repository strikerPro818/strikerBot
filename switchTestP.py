import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(13, GPIO.IN)

# GPIO.output(20, GPIO.LOW)



while True:
    if GPIO.input(13) == True:
        print("ball triggered")
    else:
        print("not triggered")
