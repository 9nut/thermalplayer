'''
Camera capture using OpenCV. This class provides
the functionality needed to run an object of this
type in its own thread. Each captured frame is forwarded
to a reciever using the Signal/Slot mechanism.

Author: skip.tavakkolian@gmail.com
'''
import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

class VidThread(QObject):
    changePixmap = pyqtSignal(QPixmap)
    go = pyqtSignal()
    width = 0
    height = 0

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
                img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = img.shape
                stride = w * ch

                qimg = QImage(img.data, w, h, stride, QImage.Format_RGB888)
                qpix = QPixmap.fromImage(qimg)
                qpix = qpix.scaled(self.width, self.height, Qt.KeepAspectRatio)
                self.changePixmap.emit(qpix)

                # Without the wait, on RPi3 we get 'too many retries' error
                QThread.msleep(100)

