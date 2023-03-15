import jetson.inference
import jetson.utils
import time

# initialize the camera
camera = jetson.utils.gstCamera(1280, 720, "/dev/video0")

# initialize the object tracker
tracker = jetson.inference.detectNet("ssd-mobilenet-v2", threshold=0.5)

# get the first image from the camera
img, width, height = camera.CaptureRGBA(zeroCopy=1)

# initialize the bounding box for tracking
bbox = jetson.utils.cudaAllocMapped(width * height * 4, "uint8")

# convert the image to RGBA format
jetson.utils.cudaConvertColor(img, jetson.utils.colorFormat.RGBA, bbox)

# set up the display
display = jetson.utils.glDisplay()

# loop through frames
while display.IsOpen():
    # capture the image from the camera
    img, width, height = camera.CaptureRGBA(zeroCopy=1)

    # convert the image to RGBA format
    jetson.utils.cudaConvertColor(img, jetson.utils.colorFormat.RGBA, bbox)

    # detect objects in the image
    detections = tracker.Detect(bbox, width, height)

    # loop through the detections
    for detection in detections:
        # get the bounding box coordinates
        left = int(detection.Left)
        top = int(detection.Top)
        right = int(detection.Right)
        bottom = int(detection.Bottom)

        # draw the bounding box on the image
        jetson.utils.cudaDrawBox(bbox, bbox, width, height, left, top, right, bottom, (255, 255, 0, 255), 3)

    # render the image
    display.RenderOnce(bbox, width, height)

    # update the window title
    display.SetTitle("Object Detection | Network {:.0f} FPS".format(tracker.GetNetworkFPS()))

    # synchronize with the GPU
    jetson.utils.cudaDeviceSynchronize()

# free the memory used for the bounding box
jetson.utils.cudaFree(bbox)
