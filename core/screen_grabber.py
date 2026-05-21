import mss
import numpy as np

class ScreenGrabber:
    def __init__(self):
        self.sct = mss.mss()

    def grab(self, rect):
        # rect: (left, top, width, height)
        monitor = {
            'left': rect[0],
            'top': rect[1],
            'width': rect[2],
            'height': rect[3]
        }
        img = self.sct.grab(monitor)
        return np.array(img)

    def close(self):
        self.sct.close()
