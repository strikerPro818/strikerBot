import jetson_inference
import jetson_utils

import argparse
import sys
import time

# Parse command line arguments
parser = argparse.ArgumentParser(description="Track humans using PedNet and Jetson Inference")
parser.add_argument("--input", type=str, default="/dev/video2", help="Input source (camera, video, or image)")
parser.add_argument("--threshold", type=float, default=0.5, help="Detection confidence threshold")
args = parser.parse_args()

# Load PedNet model
net = jetson_inference.detectNet("ped-100", threshold=args.threshold)

# Initialize video input
input_stream = jetson_utils.videoSource(args.input)

# Initialize video output
output_stream = jetson_utils.videoOutput("display://0")

# Process frames from the input source
while output_stream.IsStreaming():
    # Capture frame
    frame = input_stream.Capture()

    # Detect humans in the frame
    detections = net.Detect(frame)

    # Draw bounding boxes around detected humans
    for detection in detections:
        left = int(detection.Left)
        top = int(detection.Top)
        right = int(detection.Right)
        bottom = int(detection.Bottom)
        jetson_utils.cudaDrawRect(frame, (left, top, right, bottom), (0, 255, 0, 255))

    # Render the output frame
    output_stream.Render(frame)

    # Update the display
    output_stream.SetStatus(f"Human Tracking | {len(detections)} humans detected")

# Cleanup
input_stream.Close()
output_stream.Close()
