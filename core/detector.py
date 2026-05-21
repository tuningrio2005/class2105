import threading
from ultralytics import YOLO
import numpy as np

class Detector:
    def __init__(self, model_path=None):
        self.model = YOLO(model_path or 'yolov8n.pt')
        self.lock = threading.Lock()

    def detect(self, img):
        with self.lock:
            results = self.model(img, verbose=False)[0]
        detections = []
        for box, conf, cls in zip(results.boxes.xyxy.cpu().numpy(),
                                  results.boxes.conf.cpu().numpy(),
                                  results.boxes.cls.cpu().numpy()):
            detections.append({
                'box': box.astype(int),
                'conf': float(conf),
                'class_id': int(cls),
                'class_name': self.model.names[int(cls)]
            })
        return detections
