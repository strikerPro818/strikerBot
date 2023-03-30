import jetson_inference as ji
import jetson_utils as ju

net = ji.detectNet("facenet-120", threshold=0.5)
camera = ju.videoSource("v4l2:///dev/video2")
display = ju.videoOutput("display://0")


while display.IsStreaming():
	img = camera.Capture()
	detections = net.Detect(img)
	display.Render(img)
	display.SetStatus("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))