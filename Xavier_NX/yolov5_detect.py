# import necessary libraries
import cv2
import numpy as np

class PersonDetector:
    def __init__(self):
        # load pre-trained YOLOv3 model
        self.net = cv2.dnn.readNetFromDarknet("yolov3.cfg", "yolov3.weights")

        # get the names of the output layers
        layer_names = self.net.getLayerNames()
        self.output_layers = [layer_names[i-1] for i in self.net.getUnconnectedOutLayers()]

        # define minimum confidence level for detection
        self.conf_threshold = 0.5

    def detect(self, frame):
        # create blob from input frame
        blob = cv2.dnn.blobFromImage(frame, 1/255, (416,416), (0,0,0), True, crop=False)

        # pass blob through the network
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        # initialize lists to store detected objects and their positions
        objects = []
        positions = []

        # loop over each output layer
        for out in outs:
            # loop over each detected object
            for detection in out:
                # extract class ID and confidence level
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]

                # filter out non-person objects and objects with low confidence
                if class_id == 0 and confidence > self.conf_threshold:
                    # get object position and add to list
                    center_x = int(detection[0] * frame.shape[1])
                    center_y = int(detection[1] * frame.shape[0])
                    w = int(detection[2] * frame.shape[1])
                    h = int(detection[3] * frame.shape[0])
                    x = int(center_x - w/2)
                    y = int(center_y - h/2)
                    positions.append((x,y,w,h))

        # create list of object dictionaries with positions and confidence levels
        objects = [{"position":pos, "confidence":1} for pos in positions]

        return objects
