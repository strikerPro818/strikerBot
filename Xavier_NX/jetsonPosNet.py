import jetson_inference as ji
import jetson_utils as ju
from jetson_inference import poseNet

# initialize the pose estimation model
# posenet = ji.detectNet("resnet18-body", threshold=0.5)
net = ji.poseNet("resnet18-body", threshold=0.4)

# initialize the camera and display
camera = ju.videoSource("v4l2:///dev/video5")
display = ju.videoOutput("display://0")

# initialize the CUDA font for drawing labels
font = ju.cudaFont()

while display.IsStreaming():
    # capture a frame from the camera
    img = camera.Capture()

    # detect poses in the image
    poses = net.Process(img)

    # loop over the detected poses
    for pose in poses:
        print(pose)
        print(pose.Keypoints)
        print('Links', pose.Links)
        # get the body parts
        # keypoints = pose.Keypoints

        # TODO: process the keypoints as desired

        # draw the keypoints on the image
        # pose.Render(img)

    # display the image on the screen
    display.SetStatus("{:s} | Network {:.0f} FPS".format('PedNet', net.GetNetworkFPS()))
    # print out performance info
    net.PrintProfilerTimes()
    display.Render(img)

# release resources
camera.Close()
display.Close()
