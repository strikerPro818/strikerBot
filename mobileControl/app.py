from flask import Flask, render_template, request
import RPi.GPIO as GPIO
from src.rmd_x8 import RMD_X8
import time

# sudo ip link set can0 up type can bitrate 1000000
# sudo ifconfig can0 txqueuelen 65536

GPIO.setmode(GPIO.BCM)
robot = RMD_X8(0x141)
robot.setup()

app = Flask(__name__)

GPIO.setup(26, GPIO.OUT) #Shooter
shooter = GPIO.PWM(26, 100)
shooter.start(0)

GPIO.setup(19, GPIO.OUT) #Feeder
feeder = GPIO.PWM(19, 100)
feeder.start(0)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/set_angle', methods=['POST'])
def set_angle():
    angle = int(request.form['angle'])
    target = angle * 100 * 6;
    bb = target.to_bytes(4, 'little', signed=True)
    robot.position_closed_loop_1(bb)

    time.sleep(1)

    robot.motor_stop()
    # duty_cycle = angle / 18 + 2
    # pwm.ChangeDutyCycle(duty_cycle)
    # print(angle)
    # return "OK"

if __name__ == '__main__':
    app.run(host='192.168.31.189', port=9090, debug=True)
    # app.run(host='192.168.1.5', port=9090, debug=True)
