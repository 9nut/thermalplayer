'''
Camera capture using OpenCV. This class provides
the basic functionality to run an object of the
type in its own thread. Each captured frame is forwarded
to a reciever using the Signal/Slot mechanism.
'''
import cv2
import sys

from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class VidThread(QObject):
    changePixmap = pyqtSignal(QPixmap)
    go = pyqtSignal()
    width = 0
    height = 0
    mirror = False

    def __init__(self):
        super().__init__()
        self.go.connect(self.run)

    @pyqtSlot()
    def run(self):
        cap = cv2.VideoCapture(0)
        print("VidThread")
        while True:
            ret, frame = cap.read()
            if ret:
                if self.mirror:
                    frame = cv2.flip(frame, 1) 

                # img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # h, w, ch = img.shape
                h, w = img.shape
                ch = 1
                stride = w * ch

                # qimg = QImage(img.data, w, h, stride, QImage.Format_RGB888)
                qimg = QImage(img.data, w, h, stride, QImage.Format_Grayscale8)
                qpix = QPixmap.fromImage(qimg)
                qpix = qpix.scaled(self.width, self.height, Qt.KeepAspectRatio)
                self.changePixmap.emit(qpix)

                # Without the wait, on RPi3 we get 'too many retries' error
                QThread.msleep(100)

