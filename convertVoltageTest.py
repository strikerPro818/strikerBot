import time
import RPi.GPIO as GPIO
# import torch
# import torchvision.transforms as transforms

import math
from src.rmd_x8 import RMD_X8
# from rmd_x8 import RMD_X8
import time
from huskylib import HuskyLensLibrary
import math
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.IN)

GPIO.setup(26, GPIO.OUT)

GPIO.setup(19, GPIO.OUT)

# GPIO.setwarnings(False)

pwm = GPIO.PWM(26, 100)
pwm.start(0)

pwm2 = GPIO.PWM(19, 100)
pwm2.start(0)

GPIO.setup(13, GPIO.IN) #learn
GPIO.setup(6, GPIO.IN) #forget
GPIO.setup(5, GPIO.IN) #shoot
GPIO.setup(21, GPIO.IN) #stop

# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# midas = torch.hub.load("intel-isl/MiDaS", "MiDaS_v3_large", device).to(device)
#
# # Define image transforms
# midas_transforms = transforms.Compose(
#     [
#         transforms.Resize(256),
#         transforms.CenterCrop(256),
#         transforms.ToTensor(),
#         transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
#     ]
# )


# robot = RMD_X8(0x141)
# robot.setup()
FRAME_W = 320
FRAME_H = 240
cam_pan = 90

hl = HuskyLensLibrary("I2C", "", address=0x32)


def printObjectNicely(obj):
    count = 1
    if (type(obj) == list):
        for i in obj:
            print("\t " + ("BLOCK_" if i.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(i.__dict__))
            count += 1
    else:
        print("\t " + ("BLOCK_" if obj.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(obj.__dict__))


# pwm.stop()





# def set_duty_cycle(distance):
#     # Map the distance to a duty cycle
#     duty_cycle = (distance / 10) + 5
#     pwm.ChangeDutyCycle(duty_cycle)


# while True:
#     absoluteduty_cycle = 100
#     actual_duty_cycle = 45
#     max_duty_cycle = actual_duty_cycle * 0.45
#     min_duty_cycle = actual_duty_cycle * 0.3
#
#     pwm.ChangeDutyCycle(actual_duty_cycle)
#     time.sleep(0.1)
#     voltage = (actual_duty_cycle / 100) * (4.5 - 0.3) + 0.3
#     print(voltage)

# GPIO.cleanup()

def printObjectNicely(obj):
    count = 1
    if (type(obj) == list):
        for i in obj:
            print("\t " + ("BLOCK_" if i.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(i.__dict__))
            count += 1
    else:
        print("\t " + ("BLOCK_" if obj.type == "BLOCK" else "ARROW_") + str(count) + " : " + json.dumps(obj.__dict__))

def set_duty_cycle(distance):
    # Map the distance to a duty cycle
    # duty_cycle = ((distance / 10) + 20)
    duty_cycle = float(distance) / float(320 * 240) * 30000
    # duty_cycle = float(distance) / float(320 * 240) * 90000

    voltage = (duty_cycle / 100) * (10 - 0.3) + 0.3
    # duty =

    pwm.ChangeDutyCycle(duty_cycle)
    return duty_cycle,voltage

def calculate_distance(width, height):

    # Camera parameters


    distance =   math.sqrt(width ** 2 + height ** 2)
    print(distance)
    # distance = (FRAME_H * focal_length) / FRAME_W

    return distance



# def calculate_Distance_Pro(x, y, width, height, camera_height, image):
#     x1 = x
#     y1 = y
#     x2 = x + width
#     y2 = y + height
#
#     cropped_image = image[y1:y2, x1:x2]
#
#     # Apply transforms to the cropped image
#     input_tensor = midas_transforms(cropped_image).unsqueeze(0).to(device)
#
#     # Run the image through the MiDaS model
#     with torch.no_grad():
#         depth_map = midas(input_tensor)
#
#     # Calculate the distance from the depth map
#     distance = camera_height * 0.1 / depth_map[0, 0, height // 2, width // 2]
#
#     return distance

# Example usage
# camera_height = 2.0 # meters
# x, y, width, height = hl.blocks().x, hl.blocks().y, hl.blocks().w, hl.blocks().h
# image = hl.image()
# distance = calculate_distance(x, y, width, height, camera_height, image)








#
# while True:
#     try:
#         if (hl.learnedObjCount() > 0):
#             wData = hl.blocks().width
#             hData = hl.blocks().height
#
#
#             calculate_distance(wData,hData)
#     except:
#         print("Target Lost!")


# print("jhio")
#GPIO.setup(13, GPIO.IN) #learn
# GPIO.setup(6, GPIO.IN) #forget
# GPIO.setup(5, GPIO.IN) #shoot
# GPIO.setup(21, GPIO.IN) #stop
while True:
    try:






        if hl.learnedObjCount() > 0:
            w = hl.blocks().width
            h = hl.blocks().height
            distance = 120 - calculate_distance(w, h)



            # print(hl.blocks())
            # print(hl.blocks().width)
            # w = hl.blocks().width
            # h = hl.blocks().height
            # distance = 120 - calculate_distance(w,h)
            # distance = 60



            print("Detected Distance:",distance,'duty_cycle&voltage',set_duty_cycle(distance))
            set_duty_cycle(distance)
            if (GPIO.input(17) == True):
                print("Ball Detected!")
                pwm2.ChangeDutyCycle(100)
            else:
                pwm2.ChangeDutyCycle(0)
        else:
            print('lost')
            pwm2.ChangeDutyCycle(0)

            set_duty_cycle(0)
            # pwm.ChangeDutyCycle(30)



            # set_duty_cycle(distance)
            # print(set_duty_cycle(distance))

            # absolute_duty_cycle = 100
            # actual_duty_cycle = absolute_duty_cycle * 0.45
            # max_duty_cycle = absolute_duty_cycle * 0.45
            # min_duty_cycle = absolute_duty_cycle * 0.3
            #
            # if (GPIO.input(17) == True):
            #     print("Ball Detected!")
            #     pwm2.ChangeDutyCycle(100)
            #
            #     actual_duty_cycle = 60
            #     actual_duty_cycle = actual_duty_cycle * 0.45
            #
            #
            #
            #
            #     # pwm.ChangeDutyCycle(actual_duty_cycle)
            #     time.sleep(0.1)
            #     voltage = (actual_duty_cycle / 100) * (10 - 0.3) + 0.3
            #     print('current V:',voltage)
            # else:
            #     print("STOP!!!!")
            #     pwm2.ChangeDutyCycle(0)
            #
            #     actual_duty_cycle = 0
            #     pwm.ChangeDutyCycle(actual_duty_cycle)
    except:
        print("Target Lost")
        set_duty_cycle(0)
        pwm2.ChangeDutyCycle(0)

        None




        # print(hl.blocks().width)

        # print('hi')
    # try:
        # print("here")
        # printObjectNicely(hl)
        # w = hl.blocks().width
        # h = hl.blocks().height
        # if (hl.learnedObjCount() > 0):
        #
        #
        # # if (hl.learnedObjCount() > 0):
        #     distance = calculate_distance(calculate_distance(w,h))
        #     print('distance:',distance)
        # absolute_duty_cycle = 100
        # actual_duty_cycle = absolute_duty_cycle * 0.45
        # max_duty_cycle = absolute_duty_cycle * 0.45
        # min_duty_cycle = absolute_duty_cycle * 0.3
        #
        # if (GPIO.input(17) == False):
        #     print("Running Detected!")
        #     pwm2.ChangeDutyCycle(100)
        #
        #     actual_duty_cycle = 60
        #     actual_duty_cycle = actual_duty_cycle * 0.45
        #
        #
        #
        #
        #     pwm.ChangeDutyCycle(actual_duty_cycle)
        #     time.sleep(0.1)
        #     voltage = (actual_duty_cycle / 100) * (10 - 0.3) + 0.3
        #     print('current V:',voltage)
        # else:
        #     print("STOP!!!!")
        #     pwm2.ChangeDutyCycle(0)
        #
        #     actual_duty_cycle = 0
        #     pwm.ChangeDutyCycle(actual_duty_cycle)

    # except:
    #     None

# while(True):
#     try:
#
#
#         w = hl.blocks().width
#         h = hl.blocks().height
#         print('pass')
#         # if (hl.learnedObjCount() > 0):
#         #     distance = calculate_distance(calculate_distance(w,h))
#         #     print('distance:',distance)
#         #     absolute_duty_cycle = 100
#         #     actual_duty_cycle = absolute_duty_cycle * 0.45
#         #     max_duty_cycle = absolute_duty_cycle * 0.45
#         #     min_duty_cycle = absolute_duty_cycle * 0.3
#         #
#         #     if (GPIO.input(17) == True):
#         #         print("Running Detected!")
#         #         pwm2.ChangeDutyCycle(100)
#         #
#         #         actual_duty_cycle = 60
#         #         actual_duty_cycle = actual_duty_cycle * 0.45
#         #
#         #
#         #
#         #
#         #         pwm.ChangeDutyCycle(actual_duty_cycle)
#         #         time.sleep(0.1)
#         #         voltage = (actual_duty_cycle / 100) * (10 - 0.3) + 0.3
#         #         print('current V:',voltage)
#         #     else:
#         #         print("STOP!!!!")
#         #         pwm2.ChangeDutyCycle(0)
#         #
#         #         actual_duty_cycle = 0
#         #         pwm.ChangeDutyCycle(actual_duty_cycle)
#         # if(hl.learnedObjCount() == 0):
#         #     print("Nothing")
#
#
#     except:
#         # None
#         # print('Here')
#         pwm.stop()
#         GPIO.cleanup()
