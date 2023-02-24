from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
from src.rmd_x8 import RMD_X8
import time

# sudo ip link set can0 up type can bitrate 1000000
# sudo ifconfig can0 txqueuelen 65536

GPIO.setwarnings(False)

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
@app.route('/shoot', methods=['POST'])
def shoot():
    action = request.form['action']
    if action == 'start':
        shooter.ChangeDutyCycle(26)
        print('20')
        return jsonify(message='Shooting started')
    elif action == 'stop':
        shooter.ChangeDutyCycle(0)
        return jsonify(message='Shooting stopped')
    else:
        return jsonify(message='Invalid action')

if __name__ == '__main__':

    app.run(host='192.168.31.189', port=9090, debug=True)
    # app.run(host='192.168.1.5', port=9090, debug=True)
