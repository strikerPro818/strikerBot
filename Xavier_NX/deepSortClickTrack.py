import cv2
import torch
import numpy as np
from deep_sort.deep_sort import build_tracker
from deep_sort.utils.parser import get_config

cfg = get_config('/home/striker/Jetson/Xavier_NX/deep_sort/configs/deep_sort.yaml')

use_cuda = True
model = torch.hub.load('/home/striker/Jetson/Xavier_NX/model/',model='yolov5s',source='local').cuda()

# model = torch.hub.load('ultralytics/yolov5', 'yolov5s', force_reload=False).cuda()
tracker = build_tracker(cfg, use_cuda)

cap = cv2.VideoCapture(2, cv2.CAP_V4L2)

highlighted_id = None

def mouse_callback(event, x, y, flags, param):
    global highlighted_id
    if event == cv2.EVENT_LBUTTONDOWN:
        found_id = None
        for output in param:
            x1, y1, x2, y2, _, track_id = output
            if x1 <= x <= x2 and y1 <= y <= y2:
                found_id = int(track_id)
                break

        if highlighted_id is not None and highlighted_id == found_id:
            highlighted_id = None
        else:
            highlighted_id = found_id


cv2.namedWindow("frame")
cv2.setMouseCallback("frame", mouse_callback)

while True:
    ret, frame = cap.read()
    results = model(frame, size=640)

    bboxes = results.xywh[0][:, :4].cpu().numpy()
    confidences = results.xywh[0][:, 4].cpu().numpy()
    classes = results.xywh[0][:, 5].cpu().numpy()

    person_indices = np.where(classes == 0)
    outputs = tracker.update(bboxes[person_indices], confidences[person_indices], classes[person_indices], frame)

    for output in outputs:
        x1, y1, x2, y2, _, track_id = output
        if highlighted_id is not None and int(track_id) == highlighted_id:
            color = (0, 0, 255)
            text = f'Selected ID: {int(track_id)}'
            xywh_text = f'xywh: {x1}, {y1}, {x2 - x1}, {y2 - y1}'
        else:
            color = (0, 255, 0)
            text = f'Track ID: {int(track_id)}'
            xywh_text = ''

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        cv2.putText(frame, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        if xywh_text:
            cv2.putText(frame, xywh_text, (x1, y2 + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    cv2.imshow('frame', frame)
    cv2.setMouseCallback("frame", mouse_callback, param=outputs)

    key = cv2.waitKey(1)
    if key & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
