import cv2

# Load the overlay image
overlay_img = cv2.imread("/home/striker/Jetson/Xavier_NX/c2.png")

# Initialize the camera capture object
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)


# Loop over frames from the camera
while True:
    # Read a frame from the camera
    ret, frame = cap.read()

    # Resize the overlay image to match the size of the frame
    overlay_resized = cv2.resize(overlay_img, (frame.shape[1], frame.shape[0]))

    # Combine the frame and overlay image using cv2.addWeighted()
    alpha = 0.5  # Set the alpha value to control the opacity of the overlay
    blended = cv2.addWeighted(frame, 1 - alpha, overlay_resized, alpha, 0)

    # Display the resulting image
    cv2.imshow("Overlay", blended)

    # Check if the user pressed the 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera capture object and close all windows
cap.release()
cv2.destroyAllWindows()
