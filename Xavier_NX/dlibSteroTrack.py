import cv2
import dlib

# Create a dlib face detector object
detector = dlib.get_frontal_face_detector()

# Create a dlib tracker object
tracker = dlib.correlation_tracker()

# Initialize the video capture object
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Loop over the frames from the video stream
while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    if ret:
        # Convert the frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the grayscale frame
        faces = detector(gray)

        # Loop over the detected faces
        for face in faces:
            # Get the bounding box coordinates of the face
            x, y, w, h = face.left(), face.top(), face.width(), face.height()

            # Initialize a new tracker for the face
            tracker.start_track(frame, dlib.rectangle(x, y, x+w, y+h))

            # Draw a rectangle around the face
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # Display the resulting frame
            cv2.imshow('Frame', frame)

        # Wait for a key press
        key = cv2.waitKey(1) & 0xFF

        # If the 'q' key was pressed, break from the loop
        if key == ord('q'):
            break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
