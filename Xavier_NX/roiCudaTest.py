import cv2

# Open the default camera
cap = cv2.VideoCapture(0)

# Check if the camera is opened successfully
if not cap.isOpened():
    print("Unable to open the camera")
    exit()

# Loop through the frames
while True:
    # Capture a frame
    ret, frame = cap.read()

    # If the frame is not captured successfully, break out of the loop
    if not ret:
        break

    # Display the frame
    cv2.imshow('Live Video', frame)

    # Wait for a key press for 1 millisecond
    # If the 'q' key is pressed, break out of the loop
    if cv2.waitKey(1) == ord('q'):
        break

# Release the camera and destroy all windows
cap.release()
cv2.destroyAllWindows()
