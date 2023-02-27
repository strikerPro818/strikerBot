# from flask import Flask, render_template, request, jsonify
# import RPi.GPIO as GPIO
# from src.rmd_x8 import RMD_X8
# import time
# import threading
# #
# # sudo ip link set can0 up type can bitrate 1000000
# # sudo ifconfig can0 txqueuelen 65536
#
# GPIO.setwarnings(False)
#
# GPIO.setmode(GPIO.BCM)
# robot = RMD_X8(0x141)
# robot.setup()
#
# app = Flask(__name__)
#
# GPIO.setup(26, GPIO.OUT)
# shooter = GPIO.PWM(26, 1000)
# shooter.start(0)
# last_duty_cycle = 0
#
#
# GPIO.setup(19, GPIO.OUT)
# feeder = GPIO.PWM(19, 100)
# feeder.start(0)
#
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
#
# @app.route('/set_angle', methods=['POST'])
# def set_angle():
#     angle = int(request.form['angle'])
#     target = angle * 100 * 6;
#     bb = target.to_bytes(4, 'little', signed=True)
#     robot.position_closed_loop_1(bb)
#
#     time.sleep(1)
#
#     robot.motor_stop()
#     return jsonify(message='Angle Moved')
#
#
# def set_shooter_duty_cycle(duty_cycle):
#     shooter.ChangeDutyCycle(duty_cycle)
#
#
# def set_feeder_duty_cycle(duty_cycle):
#     feeder.ChangeDutyCycle(duty_cycle)
#
#
# def ramp_up_shooter_duty_cycle(duty_cycle):
#     current_duty_cycle = duty_cycle
#     step_size = 1
#     delay = 0.005
#     for i in range(current_duty_cycle, duty_cycle + 1, step_size):
#         set_shooter_duty_cycle(i)
#         time.sleep(delay)
#
#
# def ramp_up_feeder_duty_cycle(duty_cycle):
#     current_duty_cycle = duty_cycle
#     step_size = 1
#     delay = 0.005
#     for i in range(current_duty_cycle, duty_cycle + 1, step_size):
#         set_feeder_duty_cycle(i)
#         time.sleep(delay)
# # @app.route('/shoot', methods=['POST'])
# # def shoot():
# #     action = request.form['action']
# #     if action == 'start':
# #         # shooter.ChangeDutyCycle(13)
# #
# #         # shooter.ChangeDutyCycle(13)
# #         # print('20')
# #         # speed = int(request.form['speed'])
# #         # pwmDutyCycle = speed
# #         # shooter.ChangeDutyCycle(pwmDutyCycle)
# #         # return 'Speed set to {}'.format(speed)
# #         return jsonify(message='Shooting started')
# #     elif action == 'stop':
# #         shooter.ChangeDutyCycle(0)
# #         return jsonify(message='Shooting stopped')
# #     else:
# #         return jsonify(message='Invalid action')
# @app.route('/feed', methods=['POST'])
# def feed():
#     action = request.form['action']
#     if action == 'start':
#         # set_feeder_duty_cycle(100)
#         feeder.ChangeDutyCycle(100)
#         return jsonify(message='Feeder started')
#     elif action == 'stop':
#         feeder.ChangeDutyCycle(0)
#         return jsonify(message='Feeder stopped')
#     else:
#         return jsonify(message='Invalid action')
#
# @app.route('/set_speed', methods=['POST'])
# def shoot():
#     global last_duty_cycle
#     duty_cycle = int(request.form["speed"])
#     if duty_cycle != last_duty_cycle:
#         last_duty_cycle = duty_cycle
#         set_shooter_duty_cycle(duty_cycle)
#     return ""
#
#
#     # return 'Speed set to {}'.format(speed)
#
#
#
# if __name__ == '__main__':
#     try:
#         app.run(host='192.168.31.189', port=9090, debug=True)
#     finally:
#         shooter.stop()  # Stop the PWM
#         feeder.stop()
#         GPIO.cleanup()  # Clean up the GPIO pins
#     # app.run(host='192.168.1.5', port=9090, debug=True)


# from flask import Flask, render_template, request, jsonify
# import RPi.GPIO as GPIO
# from src.rmd_x8 import RMD_X8
# import time
# import threading
#
# GPIO.setwarnings(False)
# GPIO.setmode(GPIO.BCM)
# robot = RMD_X8(0x141)
# robot.setup()
#
# app = Flask(__name__)
#
# GPIO.setup(26, GPIO.OUT)
# shooter = GPIO.PWM(26, 1000)
# shooter.start(0)
# last_duty_cycle = 0
#
# GPIO.setup(19, GPIO.OUT)
# feeder = GPIO.PWM(19, 100)
# feeder.start(0)
#
# def set_shooter_duty_cycle(duty_cycle):
#     shooter.ChangeDutyCycle(duty_cycle)
#
# def set_feeder_duty_cycle(duty_cycle):
#     feeder.ChangeDutyCycle(duty_cycle)
#
# def ramp_up_shooter_duty_cycle(duty_cycle):
#     current_duty_cycle = duty_cycle
#     step_size = 1
#     delay = 0.005
#     for i in range(current_duty_cycle, duty_cycle + 1, step_size):
#         set_shooter_duty_cycle(i)
#         time.sleep(delay)
#
# def ramp_up_feeder_duty_cycle(duty_cycle):
#     current_duty_cycle = duty_cycle
#     step_size = 1
#     delay = 0.005
#     for i in range(current_duty_cycle, duty_cycle + 1, step_size):
#         set_feeder_duty_cycle(i)
#         time.sleep(delay)
#
# def angle_thread(angle):
#     target = angle * 100 * 6;
#     bb = target.to_bytes(4, 'little', signed=True)
#     robot.position_closed_loop_1(bb)
#     time.sleep(1)
#     robot.motor_stop()
#
# def shooter_thread(duty_cycle):
#     global last_duty_cycle
#     if duty_cycle != last_duty_cycle:
#         last_duty_cycle = duty_cycle
#         ramp_up_shooter_duty_cycle(duty_cycle)
#
# def feeder_thread(duty_cycle):
#     set_feeder_duty_cycle(duty_cycle)
#
# @app.route('/')
# def index():
#     return render_template('index.html')
#
# @app.route('/set_angle', methods=['POST'])
# def set_angle():
#     angle = int(request.form['angle'])
#     t = threading.Thread(target=angle_thread, args=(angle,))
#     t.start()
#     return jsonify(message='Angle Moved')
#
# @app.route('/feed', methods=['POST'])
# def feed():
#     action = request.form['action']
#     if action == 'start':
#         t = threading.Thread(target=feeder_thread, args=(100,))
#         t.start()
#         return jsonify(message='Feeder started')
#     elif action == 'stop':
#         feeder.ChangeDutyCycle(0)
#         return jsonify(message='Feeder stopped')
#     else:
#         return jsonify(message='Invalid action')
#
# @app.route('/set_speed', methods=['POST'])
# def shoot():
#     duty_cycle = int(request.form["speed"])
#     t = threading.Thread(target=shooter_thread, args=(duty_cycle,))
#     t.start()
#     return ""
#
# if __name__ == '__main__':
#     try:
#         app.run(host='192.168.31.189', port=9090, debug=True)
#     finally:
#         shooter.stop()  # Stop the PWM
#         feeder.stop()
#         GPIO.cleanup()  # Clean up the GPIO pins


from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
from src.rmd_x8 import RMD_X8
import time
import json
from huskylib import HuskyLensLibrary
import threading

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
robot = RMD_X8(0x141)
robot.setup()

app = Flask(__name__)

GPIO.setup(26, GPIO.OUT)
shooter = GPIO.PWM(26, 1000)
shooter.start(0)
last_duty_cycle = 0

GPIO.setup(19, GPIO.OUT)
feeder = GPIO.PWM(19, 100)
feeder.start(0)

startangle = 0
anglestarted = 0
FRAME_W = 320
FRAME_H = 240
cam_pan = 90

hl = HuskyLensLibrary("I2C", "", address=0x32)


def set_shooter_duty_cycle(duty_cycle):
    shooter.ChangeDutyCycle(duty_cycle)


def set_feeder_duty_cycle(duty_cycle):
    feeder.ChangeDutyCycle(duty_cycle)


def ramp_up_shooter_duty_cycle(duty_cycle):
    current_duty_cycle = duty_cycle
    step_size = 1
    delay = 0.005
    for i in range(current_duty_cycle, duty_cycle + 1, step_size):
        set_shooter_duty_cycle(i)
        time.sleep(delay)


def ramp_up_feeder_duty_cycle(duty_cycle):
    current_duty_cycle = duty_cycle
    step_size = 1
    delay = 0.005
    for i in range(current_duty_cycle, duty_cycle + 1, step_size):
        set_feeder_duty_cycle(i)
        time.sleep(delay)


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
    return jsonify(message='Angle Moved')


class ShootThread(threading.Thread):
    def __init__(self, duty_cycle):
        threading.Thread.__init__(self)
        self.duty_cycle = duty_cycle

    def run(self):
        global last_duty_cycle
        duty_cycle = self.duty_cycle
        if duty_cycle != last_duty_cycle:
            last_duty_cycle = duty_cycle
            set_shooter_duty_cycle(duty_cycle)


@app.route('/set_speed', methods=['POST'])
def shoot():
    duty_cycle = int(request.form["speed"])
    ShootThread(duty_cycle).start()
    return ""


class FeedThread(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        action = self.action
        if action == 'start':
            feeder.ChangeDutyCycle(100)
        elif action == 'stop':
            feeder.ChangeDutyCycle(0)


class LearnThread(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        action = self.action
        if action == 'start':
            pass

        elif action == 'stop':
            feeder.ChangeDutyCycle(0)


@app.route('/feed', methods=['POST'])
def feed():
    action = request.form['action']
    FeedThread(action).start()
    return jsonify(message='Feeder ' + action + 'ed')


@app.route('/learn', methods=['POST'])
def feed():
    action = request.form['action']
    FeedThread(action).start()
    return jsonify(message='Learned ' + action + 'ed')


if __name__ == '__main__':
    try:
        app.run(host='192.168.31.189', port=9090, debug=True)
    finally:
        shooter.stop()  # Stop the PWM
        feeder.stop()
        GPIO.cleanup()  # Clean up the GPIO pins
