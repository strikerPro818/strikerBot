import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

GPIO.setup(33, GPIO.IN)

# GPIO.output(20, GPIO.LOW)



while True:
    if GPIO.input(33) == True:
        print("ball triggered")
    else:
        print("not triggered")

# Clean up the GPIO pins
GPIO.cleanup()
