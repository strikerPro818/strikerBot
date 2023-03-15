import numpy as np
import cv2

# Define the size of the calibration target grid (in chessboard corners)
grid_size = (9, 6)

# Define the real-world size of each square in the grid (in meters)
square_size = 0.025

# Create a list to store the calibration images
calibration_imgs = []

# Capture calibration images using your stereo camera and append them to the list
# ...

# Define the world points for the calibration target
world_points = np.zeros((np.prod(grid_size), 3), dtype=np.float32)
world_points[:, :2] = np.mgrid[0:grid_size[0], 0:grid_size[1]].T.reshape(-1, 2) * square_size

# Define the image points for the calibration images
left_image_points = []
right_image_points = []

# Detect the chessboard corners in each calibration image
for img in calibration_imgs:
    # Split the stereo image into left and right images
    height, width, channels = img.shape
    left_img = img[:, :int(width/2), :]
    right_img = img[:, int(width/2):, :]

    # Find the chessboard corners in both left and right images
    ret_left, corners_left = cv2.findChessboardCorners(left_img, grid_size, None)
    ret_right, corners_right = cv2.findChessboardCorners(right_img, grid_size, None)

    # If corners are found in both images, append them to the image points list
    if ret_left and ret_right:
        left_image_points.append(corners_left)
        right_image_points.append(corners_right)

# Calculate the camera matrices and distortion coefficients for both cameras
flags = cv2.CALIB_FIX_INTRINSIC | cv2.CALIB_USE_INTRINSIC_GUESS
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
_, left_matrix, left_distortion, right_matrix, right_distortion, _, _ = cv2.stereoCalibrate(
    objectPoints=[world_points]*len(left_image_points),
    imagePoints1=left_image_points,
    imagePoints2=right_image_points,
    imageSize=(width, height),
    cameraMatrix1=np.eye(3),
    distCoeffs1=np.zeros(5),
    cameraMatrix2=np.eye(3),
    distCoeffs2=np.zeros(5),
    flags=flags,
    criteria=criteria
)

# Average the camera matrices and use the average as the intrinsic camera matrix
intrinsic_matrix = (left_matrix + right_matrix) / 2

# Print the intrinsic matrix
print("Intrinsic camera matrix:")
print(intrinsic_matrix)
