import cv2
import tensorflow.compat.v1 as tf
from mtcnn import MTCNN

# Disable TensorFlow v2 behavior
tf.disable_v2_behavior()

# Create a TensorFlow session configuration with GPU acceleration
config = tf.ConfigProto()
config.gpu_options.allow_growth = True

# Start a TensorFlow session with the above configuration
sess = tf.Session(config=config)

# Initialize the MTCNN face detector
detector = MTCNN()

# Start capturing frames from the camera
camera = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Loop over the frames from the camera
while True:
    # Capture a frame from the camera
    ret, frame = camera.read()

    # Resize the frame to a smaller size
    frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

    # Convert the frame to RGB
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # Detect faces in the frame using MTCNN
    faces = detector.detect_faces(frame)

    # Loop over the detected faces
    for face in faces:
        # Get the bounding box coordinates of the face
        x, y, w, h = face['box']

        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Display the bounding box coordinates of the face on the screen
        text = f"({x}, {y}), width={w}, height={h}"
        cv2.putText(frame, text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Display the current frame
    cv2.imshow('Face Detector', cv2.resize(frame, (1920, 1080)))

    # Wait for a key press
    key = cv2.waitKey(1)

    # Exit the loop if the 'q' key is pressed
    if key == ord('q'):
        break

# Release the camera and close all windows
camera.release()
cv2.destroyAllWindows()
