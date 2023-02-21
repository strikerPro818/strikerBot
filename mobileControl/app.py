from flask import Flask, render_template, request
import RPi.GPIO as GPIO

app = Flask(__name__)

# Set up GPIO pins
GPIO.setmode(GPIO.BOARD)
GPIO.setup(12, GPIO.OUT)
pwm = GPIO.PWM(12, 50)
pwm.start(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_angle', methods=['POST'])
def set_angle():
    angle = int(request.form['angle'])
    duty_cycle = angle / 18 + 2
    pwm.ChangeDutyCycle(duty_cycle)
    return "OK"

if __name__ == '__main__':
    app.run(host='192.168.31.189', port=9090, debug=True)
    # app.run(host='192.168.1.5', port=9090, debug=True)
