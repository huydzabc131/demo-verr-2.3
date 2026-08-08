import time
import os
import cv2

from PySide6.QtCore import QThread, Signal

from core.adb import screenshot


class ScreenThread(QThread):

    frame_changed = Signal(object)

    def __init__(self, device):
        super().__init__()

        self.device = device
        self.running = False

    def run(self):

        self.running = True

        while self.running:
            try:
                path = screenshot(self.device, "live")

                if os.path.exists(path):
                    frame = cv2.imread(path)

                    if frame is not None and frame.size > 0:
                        self.frame_changed.emit(frame)
            except Exception as e:
                print("ScreenThread frame capture error:", e)

            time.sleep(0.3)      # khoảng 3 FPS

    def stop(self):
        self.running = False