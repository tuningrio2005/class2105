import threading
import queue
import pyttsx3

class TTSWorker(threading.Thread):
    def __init__(self, mute=False):
        super().__init__(daemon=True)
        self.q = queue.Queue()
        self.engine = pyttsx3.init()
        self.mute = mute
        self._stop = threading.Event()

    def run(self):
        while not self._stop.is_set():
            try:
                phrase = self.q.get(timeout=0.2)
                if not self.mute:
                    self.engine.say(phrase)
                    self.engine.runAndWait()
            except queue.Empty:
                continue

    def speak(self, phrase):
        self.q.put(phrase)

    def set_mute(self, mute):
        self.mute = mute

    def stop(self):
        self._stop.set()
        self.engine.stop()
