import torch
import cv2
import time

model = torch.hub.load('/home/striker/.local/lib/python3.8/site-packages/yolov5/', 'custom',
                       path='/home/striker/.local/lib/python3.8/site-packages/yolov5/yolov5s.engine',
                       source='local').cuda().eval()

# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False).cuda().eval()

# cap = cv2.VideoCapture(0)
# overlay_img = cv2.imread("/home/striker/Jetson/Xavier_NX/c2.png")
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)
# cap = cv2.VideoCapture(3)
frame_count = 0
start_time = time.time()
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # overlay_resized = cv2.resize(overlay_img, (frame.shape[1], frame.shape[0]))

    # Combine the frame and overlay image using cv2.addWeighted()

    # Detect humans using YOLOv5
    frame_resized = cv2.resize(frame, (640, 640))

    results = model(frame_resized)

    # Get the coordinates of the detected humans
    boxes = results.xyxy[0].cpu().numpy()

    # Draw bounding boxes around the detected humans and show the x, y, height and width
    for box in boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame_resized, (x1, y1), (x2, y2), (0, 255, 0), 2)
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            cv2.putText(frame_resized, f'x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(f"x: {x1}, y: {y1}, width: {x2 - x1}, height: {y2 - y1}")
            # alpha = 0.45  # Set the alpha value to control the opacity of the overlay
            # blended = cv2.addWeighted(frame, 1 - alpha, overlay_resized, alpha, 0)
    end_time = time.time()
    elapsed_time = end_time - start_time
    fps = frame_count / elapsed_time
    fps_text = f"FPS: {fps:.2f}"
    cv2.putText(frame_resized, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('frame', frame_resized)
    # Increment frame count and update timer
    frame_count += 1
    if frame_count % 10 == 0:  # Calculate fps every 10 frames
        frame_count = 0
        start_time = time.time()
    # cv2.imshow("Overlay", blended)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



