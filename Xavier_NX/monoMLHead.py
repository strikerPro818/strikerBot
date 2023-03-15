import torch
import cv2
import numpy as np
from PIL import Image as pil

# Load the MiDaS model
model = torch.hub.load("intel-isl/MiDaS", "MiDaS_small", pretrained=True)
device = torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")
model.to(device)
model.eval()

# Set camera resolution
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Define camera intrinsic parameters
focal_length = 2.26  # mm
fov = 130  # degrees
sensor_width = 3.68  # mm
sensor_height = 2.76  # mm
camera_height = 0.9  # meters

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()

    # Resize the frame to the expected input size of the MiDaS model
    frame = cv2.resize(frame, (384, 384), interpolation=cv2.INTER_LINEAR)

    # Convert the image to a PIL image and run the MiDaS model
    frame_pil = pil.fromarray(frame)
    with torch.no_grad():
        frame_torch = torch.from_numpy(np.asarray(frame_pil)).unsqueeze(0).permute(0, 3, 1, 2).float().to(device)
        depth = model(frame_torch)

    # Convert the depth map to a grayscale image and normalize the pixel values
    depth_np = depth.squeeze().cpu().numpy()
    depth_gray = cv2.normalize(np.array(depth_np * 255), None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)

    # Compute the distance to the object in meters
    depth_meters = depth_np.mean() / 1000.0
    object_width = 1.0
    distance = focal_length * object_width / depth_meters

    # Display distance information
    cv2.putText(frame, f'distance: {distance:.2f} m', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the resulting frames
    cv2.imshow('frame', frame)
    cv2.imshow('depth', depth_gray)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
