import cv2
import torch
import torchvision

# Load the pre-trained Faster R-CNN model
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()

# Set up the video capture
cap = cv2.VideoCapture(0, cv2.CAP_V4L2)

# Set the resolution of the input image
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

while True:
    # Read a frame from the video stream
    ret, frame = cap.read()

    # Preprocess the frame
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame = torch.from_numpy(frame).permute(2, 0, 1)
    frame = frame.float() / 255.0
    frame = frame.unsqueeze(0)

    # Detect faces
    with torch.no_grad():
        outputs = model(frame)

    # Draw bounding boxes around detected faces
    boxes = outputs[0]['boxes']
    scores = outputs[0]['scores']
    for i, score in enumerate(scores):
        if score > 0.5:
            x1, y1, x2, y2 = boxes[i].tolist()
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)

    # Display the frame
    frame = frame.squeeze(0).permute(1, 2, 0).numpy()
    cv2.imshow('frame', frame)

    # Wait for a key press
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close the window
cap.release()
cv2.destroyAllWindows()
