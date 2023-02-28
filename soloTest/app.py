from flask import Flask, render_template, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__)
GPIO.setmode(GPIO.BCM)
GPIO.setup(19, GPIO.OUT)
pwm = GPIO.PWM(19, 1000)
pwm.start(0)
last_duty_cycle = 0

def set_duty_cycle(duty_cycle):
    pwm.ChangeDutyCycle(duty_cycle)

def ramp_up_duty_cycle(duty_cycle):
    current_duty_cycle = duty_cycle
    step_size = 1
    delay = 0.005
    for i in range(current_duty_cycle, duty_cycle + 1, step_size):
        set_duty_cycle(i)
        time.sleep(delay)


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_duty_cycle", methods=["POST"])
def set_duty_cycle_route():
    global last_duty_cycle
    duty_cycle = int(request.form["duty_cycle"])
    if duty_cycle != last_duty_cycle:
        last_duty_cycle = duty_cycle
        ramp_up_duty_cycle(duty_cycle)
    return ""

if __name__ == "__main__":
    try:
        app.run(host='192.168.31.189', port=9090, debug=True)
    finally:
        pwm.stop()  # Stop the PWM
        GPIO.cleanup()  # Clean up the GPIO pins
