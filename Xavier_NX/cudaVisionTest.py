import torch
import cv2
model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False)
model.cuda()
# cap = cv2.VideoCapture(0)
# overlay_img = cv2.imread("/home/striker/Jetson/Xavier_NX/c2.png")
cap = cv2.VideoCapture(5, cv2.CAP_V4L2)
# cap = cv2.VideoCapture(3)

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    # overlay_resized = cv2.resize(overlay_img, (frame.shape[1], frame.shape[0]))

    # Combine the frame and overlay image using cv2.addWeighted()

    # Detect humans using YOLOv5
    results = model(frame, size=640)

    # Get the coordinates of the detected humans
    boxes = results.xyxy[0].cpu().numpy()

    # Draw bounding boxes around the detected humans and show the x, y, height and width
    for box in boxes:
        if box[5] == 0:  # Class index for humans is 0
            x1, y1, x2, y2 = map(int, box[:4])
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            x, y, w, h = x1, y1, x2 - x1, y2 - y1
            cv2.putText(frame, f'x:{x}, y:{y}, w:{w}, h:{h}', (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(f"x: {x1}, y: {y1}, width: {x2 - x1}, height: {y2 - y1}")
            # alpha = 0.45  # Set the alpha value to control the opacity of the overlay
            # blended = cv2.addWeighted(frame, 1 - alpha, overlay_resized, alpha, 0)
    # Display t
    # he resulting frame
    cv2.imshow('frame', frame)
    # cv2.imshow("Overlay", blended)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()



