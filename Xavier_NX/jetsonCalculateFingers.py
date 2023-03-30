import jetson_inference as ji
import jetson_utils as ju
from jetson_inference import poseNet

import Jetson.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setup(33, GPIO.OUT)

shooter = GPIO.PWM(33, 100)
shooter.start(0)

# GPIO.setmode(GPIO.BOARD)
# GPIO.setup(32, GPIO.OUT)
#
# feeder = GPIO.PWM(32, 100)
# feeder.start(0)

# initialize the pose estimation model
net = ji.poseNet("resnet18-hand", threshold=0.3)

# initialize the camera and display
# camera = ju.videoSource("v4l2:///dev/video5", argv=['--input-format=yuyv', '--input-width=1920', '--input-height=1080', '--input-fps=60'])
camera = ju.videoSource("v4l2:///dev/video0", argv=[ '--input-fps=30'])
display = ju.videoOutput("display://0")
# initialize the CUDA font for drawing labels
font = ju.cudaFont()

def setShooterSpeed(speed):
    # while True:
    speed = shooter.ChangeDutyCycle(speed)
    print('Shooter Duty cycle:',speed)
    time.sleep(0.01)

def setFeederSpeed(speed):
    # while True:
    speed = shooter.ChangeDutyCycle(speed)
    print('Feeder Duty cycle:', speed)
    time.sleep(0.01)

    # print("Current duty cycle: {:.2f}".format(duty_cycle))
    # time.sleep(0.1)
def euclidean_distance(a, b):
    return ((a.x - b.x)**2 + (a.y - b.y)**2)**0.5


def is_palm_open(pose):
    palm = pose.Keypoints[0]
    extended_fingers = 0

    # Loop over the fingertips
    for fingertip_idx in [4, 8, 12, 16, 20]:
        fingertip = pose.Keypoints[fingertip_idx]
        distance = euclidean_distance(palm, fingertip)

        if distance > 50:  # Adjust this threshold as needed
            extended_fingers += 1

    return extended_fingers >= 4

while display.IsStreaming():
    # capture a frame from the camera
    img = camera.Capture()

    # detect poses in the image
    poses = net.Process(img)

    # loop over the detected poses
    for pose in poses:
        if len(pose.Keypoints) == 21:
            palm_open = is_palm_open(pose)
            print("Palm open:", palm_open)

            # Get the bounding box for the hand
            x_coords = [kp.x for kp in pose.Keypoints]
            y_coords = [kp.y for kp in pose.Keypoints]
            left = min(x_coords)
            top = min(y_coords)
            right = max(x_coords)
            bottom = max(y_coords)
            bb = (int(left), int(top), int(right - left), int(bottom - top))
            print(bb)
            print(int(left),int(top))
            # print(bb[0][0])

            # Set the color and text based on the palm_open status
            if palm_open:
                # colorInput = font.Red
                text = "Fired!"
                print(text,'Red')
                font.OverlayText(img,img.width,img.height,text,800,200,font.Orange,font.Gray40)

                setShooterSpeed(27)
                # setFeederSpeed(100)

                # time.sleep(0.5)

            else:
                # colorInput = font.Green
                setShooterSpeed(0)
                # setFeederSpeed(0)


                text2 = "Not Opened Fully"
                print(text2)

            # Draw the rectangle around the hand
            # ju.cudaDrawRect(img, bb, color)

            # # Draw the "Fired!" text if the palm is open
            # if text:
            #     print(img.width, img.height)
            #     font.OverlayText(img,img.width,img.height,text,800,200,font.Red)
            #     print(text,colorInput)





        else:
            # font.OverlayText(img, img.width, img.height, 'Not Ready', 800, 200, font.Blue)
            setShooterSpeed(0)
            # setFeederSpeed(0)

            print("Not all keypoints are detected")

    # display the image on the screen
    display.SetStatus("VideoFPS {:.0f}  FPS {:.0f} ".format(display.GetFrameRate(), net.GetNetworkFPS()))
    net.PrintProfilerTimes()
    display.Render(img)

# release resources
camera.Close()
display.Close()
