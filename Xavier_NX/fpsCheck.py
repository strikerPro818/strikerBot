import cv2

# Open the V4L2 device
cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

# Check if the V4L2 device was opened successfully
if not cap.isOpened():
    print("Failed to open V4L2 device")
    exit()

# Set the capture format
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

# Initialize variables for FPS calculation
prev_time = 0
fps = 0

# Capture frames from the V4L2 device, down-sample them, and add FPS information
while True:
    # Read a frame from the V4L2 device
    ret, frame = cap.read()

    # Check if the frame was read successfully
    if not ret:
        print("Failed to read frame from V4L2 device")
        break

    # Down-sample the frame to 640x480 resolution
    resized_frame = cv2.resize(frame, (640, 480))

    # Calculate the current FPS
    current_time = cv2.getTickCount()
    time_diff = (current_time - prev_time) / cv2.getTickFrequency()
    prev_time = current_time
    fps = 1 / time_diff

    # Add FPS information to the down-sampled frame
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(resized_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    # Process the down-sampled frame (e.g. display it, save it to disk, etc.)
    cv2.imshow("Resized Frame", resized_frame)

    # Wait for a key press and check if the 'q' key was pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the V4L2 device and close the OpenCV window
cap.release()
cv2.destroyAllWindows()
