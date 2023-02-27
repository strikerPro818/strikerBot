import RPi.GPIO as GPIO
import time
GPIO.setwarnings(False)


# Set GPIO mode to BCM
GPIO.setmode(GPIO.BCM)

# Set pin 18 as PWM output with 50 Hz frequency
GPIO.setup(21, GPIO.OUT)
pwm = GPIO.PWM(21, 50)
pwm.start(0)

try:
    while True:
        # Increase duty cycle from 0 to 100
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)

        # Decrease duty cycle from 100 to 0
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.1)

except KeyboardInterrupt:
    # Clean up GPIO pins on keyboard interrupt
    pwm.stop()
    GPIO.cleanup()
