import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(21, GPIO.IN)

# GPIO.output(20, GPIO.LOW)



while True:
    if GPIO.input(21) == True:
        print("Triggered")
    else:
        print("NO")
