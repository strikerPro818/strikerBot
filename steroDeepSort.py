import sys
import cv2
import torch
from yolov5.models.experimental import attempt_load
from yolov5.utils.general import non_max_suppression, scale_coords
from deep_sort_pytorch.deep_sort import DeepSort
from deep_sort_pytorch.utils.parser import get_config


def track_people(video_path, output_path):
    # Load YOLOv5s model
    model = attempt_load("yolov5s.pt", map_location=torch.device('cpu'))

    # Initialize DeepSORT
    cfg = get_config()
    deepsort = DeepSort(cfg.DEEPSORT.REID_CKPT)

    # Open video file
    cap = cv2.VideoCapture(2, cv2.CAP_V4L2)


    # Define codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    while True:
        # Read a frame from the video file
        ret, frame = cap.read()
        if not ret:
            break

        # Detect objects using YOLOv5s
        results = model(frame[:, :, ::-1], size=640)
        results = non_max_suppression(results.pred, conf_thres=0.4, iou_thres=0.5, classes=[0])  # class 0 is person

        # Prepare inputs for DeepSORT
        if results:
            bboxes = results[0][:, :4].cpu().numpy()
            confs = results[0][:, 4].cpu().numpy()
            bboxes[:, :4] = scale_coords((640, 640), bboxes[:, :4], frame.shape[:2]).round()
        else:
            bboxes = []
            confs = []

        # Update tracker with the new detections
        outputs = deepsort.update(bboxes, confs, frame)

        # Draw bounding boxes and track IDs on the frame
        for output in outputs:
            bbox = output[:4].astype(int)
            track_id = output[4]
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), (0, 255, 0), 2)
            cv2.putText(frame, str(track_id), (bbox[0], bbox[1] - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # Write the frame to the output video file
        writer.write(frame)

    # Release video file and output video writer
    cap.release()
    writer.release()
