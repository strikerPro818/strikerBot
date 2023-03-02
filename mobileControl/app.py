from flask import Flask, render_template, request, jsonify
import RPi.GPIO as GPIO
from src.rmd_x8 import RMD_X8
import time
import json
from huskylib import HuskyLensLibrary
import threading
import os

os.system('sudo ip link set can0 up type can bitrate 1000000')
os.system('sudo ifconfig can0 txqueuelen 65536')

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
robot = RMD_X8(0x141)
robot.setup()

app = Flask(__name__)

GPIO.setup(26, GPIO.OUT)
shooter = GPIO.PWM(26, 1000)
shooter.start(0)
last_duty_cycle = 0


GPIO.setup(19,GPIO.OUT)
GPIO.output(19,GPIO.LOW)

GPIO.setup(4, GPIO.OUT)
feeder = GPIO.PWM(4, 100)
feeder.start(0)
feederInput = GPIO.setup(13,GPIO.IN)


GPIO.setup(21,GPIO.IN)
GPIO.setup(20,GPIO.IN)
GPIO.setup(16,GPIO.IN)
GPIO.setup(12,GPIO.IN)



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
def panAngle(inputAngle):


    angle = inputAngle
    target = int(angle * 100 * 6);
    bb = target.to_bytes(4, 'little', signed=True)
    robot.position_closed_loop_1(bb)

    # time.sleep(1)

    # robot.motor_stop()

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

# class ShootThread(threading.Thread):
#     def __init__(self, duty_cycle):
#         threading.Thread.__init__(self)
#         self.duty_cycle = duty_cycle
#
#     def run(self):
#         set_shooter_duty_cycle(100)
class FeedThread(threading.Thread):

    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        action = self.action
        if action == 'start':
            GPIO.output(19, GPIO.HIGH)

            # set_feeder_duty_cycle(100)
            # feeder.ChangeDutyCycle(100)
        elif action == 'stop':
            GPIO.output(19, GPIO.LOW)

            # set_feeder_duty_cycle(0)
            # feeder.ChangeDutyCycle(0)
class LearnThread(threading.Thread):
    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        try:
            action = self.action
            if action == 'start':
                hl.learn(1)
                print(hl.count())
                # time.sleep(3)
                # print('stop learnning')
                # break

            elif action == 'stop':
                hl.forget()
                print('stop learning!')
        except AttributeError and IOError:
            print("Expected Error")

class TrackThread(threading.Thread):

    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        # flag = True
        cam_pan = 90
        # hl.learn(1)
        # print(hl.count())

        action = self.action
        if action == 'start':
            while True:
                try:
                    x = hl.blocks().x
                    w = hl.blocks().width
                    if hl.learnedObjCount() > 0:
                        print(hl.count())
                        print(x, w)
                        x = x + (w / 2)
                        turn_x = float(x - (FRAME_W / 2))
                        turn_x /= float(FRAME_W / 2)
                        turn_x *= 1.2  # VFOV
                        cam_pan += -turn_x
                        print('Move: ', cam_pan - 90)
                        cam_pan = max(0, min(180, cam_pan))
                        # print('cam_pan',cam_pan)
                        panAngle(int(cam_pan - 90))
                        print('Finished Adjusting')



                        # robot.motor_stop()
                except AttributeError and IOError and IndexError:
                    robot.motor_stop()


                    continue


        if action =='stop':
            try:
                # flag = False
                hl.forget()
                robot.motor_stop()
            except AttributeError:
                print('noraml fuck')
                # print("Expected Error")


class VoiceThread(threading.Thread):

    def __init__(self, action):
        threading.Thread.__init__(self)
        self.action = action

    def run(self):
        action = self.action
        if action == 'start':
            while True:
            # GPIO.output(19, GPIO.HIGH)
                if GPIO.input(21) == True:
                    print('shoot')
                    shooter.ChangeDutyCycle(30)
                    break
                if GPIO.input(20) == True:
                    print('not shoot')
                    shooter.ChangeDutyCycle(0)
                    break

                if GPIO.input(16) == True:
                    print('feed')
                    # GPIO.output(19, GPIO.HIGH)
                    break
                if GPIO.input(12) == True:
                    print('not feed')
                    GPIO.output(19, GPIO.LOW)
                    break

            # GPIO.output(19, GPIO.HIGH)

        # if shooterVoice == True:
            #     shooter.ChangeDutyCycle(30)
            # else:
            #     print('not shoot')
            #     shooter.ChangeDutyCycle(0)
            # if fireEnableVoice == True:
            #     GPIO.output(19, GPIO.HIGH)
            # else:
            #     print('not fire')
            #
            #     GPIO.output(19, GPIO.LOW)




        elif action == 'stop':
            print('fuck you')
            # GPIO.output(19, GPIO.LOW)

            # GPIO.output(19, GPIO.LOW)

            # print('stop')
            # GPIO.output(19, GPIO.LOW)
@app.route('/feed', methods=['POST'])
def feed():
    action = request.form['action']
    FeedThread(action).start()
    return jsonify(message='Feeder ' + action + 'ed')
@app.route('/learn', methods=['POST'])
def learn():
    action = request.form['action']
    LearnThread(action).start()
    return jsonify(message='Learn ' + action + 'ed')

@app.route('/track', methods=['POST'])
def autoTrack():
    action = request.form['action']
    TrackThread(action).start()
    return jsonify(message='Track ' + action + 'ed')
@app.route('/voice', methods=['POST'])
def voiceControl():
    action = request.form['action']
    VoiceThread(action).start()
    return jsonify(message='Voice ' + action + 'ed')


if __name__ == '__main__':
    try:
        app.run(host='192.168.31.190', port=9090, debug=True)
        # app.run(host='172.20.10.3', port=9090, debug=True)

    finally:
        shooter.stop()  # Stop the PWM
        feeder.stop()
        GPIO.cleanup()  # Clean up the GPIO pins
