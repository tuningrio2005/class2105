import sys
import os
import time
import threading
from PyQt6.QtWidgets import QApplication, QFileDialog
from PyQt6.QtCore import QRect, QTimer, pyqtSignal, QObject
from ui.control_panel import ControlPanel
from ui.capture_frame import CaptureFrame
from core.detector import Detector
from core.screen_grabber import ScreenGrabber
from core.tts_worker import TTSWorker
import cv2
import numpy as np
from PIL import Image

CAPTURED_DIR = os.path.join(os.path.dirname(__file__), 'captured')
os.makedirs(CAPTURED_DIR, exist_ok=True)

class DetectionWorker(QObject, threading.Thread):
    update_counters = pyqtSignal(dict)
    update_fps = pyqtSignal(float)
    def __init__(self, frame_widget, detector, grabber, tts, get_targets, cooldown=2.0):
        QObject.__init__(self)
        threading.Thread.__init__(self, daemon=True)
        self.frame_widget = frame_widget
        self.detector = detector
        self.grabber = grabber
        self.tts = tts
        self.get_targets = get_targets
        self.cooldown = cooldown
        self.running = False
        self.counters = {}
        self.last_capture = {}
        self.fps = 0

    def run(self):
        self.running = True
        prev_time = time.time()
        while self.running:
            t0 = time.time()
            rect = self.frame_widget.geometry()
            x, y, w, h = rect.x(), rect.y(), rect.width(), rect.height()
            img = self.grabber.grab((x, y, w, h))
            img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            detections = self.detector.detect(img_bgr)
            targets = set(self.get_targets())
            now = time.time()
            for det in detections:
                name = det['class_name'].lower()
                conf = det['conf']
                if name in targets and conf >= 0.5:
                    last = self.last_capture.get(name, 0)
                    if now - last > self.cooldown:
                        self.last_capture[name] = now
                        self.counters[name] = self.counters.get(name, 0) + 1
                        self.update_counters.emit(self.counters.copy())
                        # Draw box
                        box = det['box']
                        img_box = img_bgr.copy()
                        cv2.rectangle(img_box, (box[0], box[1]), (box[2], box[3]), (108,255,99), 2)
                        cv2.putText(img_box, f"{name} {conf:.2f}", (box[0], box[1]-8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (108,255,99), 2)
                        # Save
                        ts = time.strftime('%Y%m%d_%H%M%S')
                        ms = int((now-int(now))*1000)
                        fname = f"{name}_{ts}_{ms}.png"
                        fpath = os.path.join(CAPTURED_DIR, fname)
                        Image.fromarray(cv2.cvtColor(img_box, cv2.COLOR_BGR2RGB)).save(fpath)
                        # TTS
                        self.tts.speak(name)
            t1 = time.time()
            self.fps = 1/(t1-t0) if t1 > t0 else 0
            self.update_fps.emit(self.fps)
            # Sleep to ~5-10 FPS
            delay = max(0.1, 0.2 - (t1-t0))
            time.sleep(delay)

    def stop(self):
        self.running = False

class App:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.panel = ControlPanel()
        self.frame = CaptureFrame()
        self.detector = Detector()
        self.grabber = ScreenGrabber()
        self.tts = TTSWorker()
        self.worker = None
        self.targets = []
        self.panel.start_detection.connect(self.start_detection)
        self.panel.stop_detection.connect(self.stop_detection)
        self.panel.open_captured.connect(self.open_captured)
        self.panel.mute_changed.connect(self.tts.set_mute)
        self.frame.geometry_changed.connect(self.on_frame_geometry)
        self.tts.start()
        self.panel.show()
        self.frame.show()
        self.frame.move(400, 200)
        self.frame.raise_()
        self.panel.raise_()

    def start_detection(self, targets):
        self.targets = targets
        self.worker = DetectionWorker(self.frame, self.detector, self.grabber, self.tts, lambda: self.targets)
        self.worker.update_counters.connect(self.panel.update_counters)
        self.worker.update_fps.connect(self.frame.update_fps)
        self.worker.start()

    def stop_detection(self):
        if self.worker:
            self.worker.stop()
            self.worker = None

    def open_captured(self):
        QFileDialog.getOpenFileName(self.panel, 'Open captured folder', CAPTURED_DIR)

    def on_frame_geometry(self, rect):
        pass  # Could be used for live updates

    def run(self):
        try:
            sys.exit(self.app.exec())
        finally:
            self.cleanup()

    def cleanup(self):
        if self.worker:
            self.worker.stop()
        self.tts.stop()
        self.grabber.close()

if __name__ == '__main__':
    App().run()
