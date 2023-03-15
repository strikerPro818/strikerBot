import numpy as np
from deep_sort.utils.parser import get_config
from deep_sort.deep_sort import DeepSort


class DeepSortTracker:
    """
    DeepSort object tracker.
    """

    def init(self, reid_model_path, max_dist=0.2, min_confidence=0.3, nms_max_overlap=1.0,
             max_iou_distance=0.7, max_age=70, n_init=3, nn_budget=None, use_cuda=True):
        self.deepsort = DeepSort(reid_model_path, max_dist=max_dist, min_confidence=min_confidence,
                                 nms_max_overlap=nms_max_overlap, max_iou_distance=max_iou_distance,
                                 max_age=max_age, n_init=n_init, nn_budget=nn_budget, use_cuda=use_cuda)

    def update(self, detections, iou_threshold):
        detection_list = []
        for detection in detections:
            bbox = detection[:4]
            confidence = detection[4]
            detection_list.append(bbox + [confidence])
        detection_array = np.array(detection_list)

        outputs = self.deepsort.update(detection_array, iou_threshold)

        tracks = []
        for output in outputs:
            bbox = output[:4]
            track_id = int(output[4])
            tracks.append(bbox + [track_id])

        return tracks
