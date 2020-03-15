'''
Player to mix Pi camera output with the mlx90640 thermal camera output.
Each capture is run in its own thread and their output (received using
Signal/Slot mechanism) are combined in the player thread. The refersh
happends on the receiver of the Pi camera since it has a faster capture
rate. A mutex is used to serialize access to thermal image pixmap.

Author: skip.tavakkolian@gmail.com
'''
import cv2
import sys
import threading
import copy

from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QThread, Qt, pyqtSignal, pyqtSlot, QPoint, QSize
from PyQt5.QtGui import QImage, QPixmap, QPainter

from PIL import Image

from pixread import VidThread
from mlxread import MLXThread

class ThermalPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'Thermal Cam'
        self.left = 50
        self.top = 50
        self.leftmargin = 100
        self.topmargin = 50
        self.width = 640
        self.height = 480
        self.heatpix = None
        self.campix = None
        self.heatpixlock = threading.Lock()
        self.initUI()


    @pyqtSlot(QPixmap)
    def setImage(self, pixmap):
        # Currently campix isn't used, but if used
        # it needs to be deep copied.
        self.campix = pixmap.copy()
        dispix = pixmap

        # Image compositing
        painter = QPainter(dispix)
        painter.setRenderHint(QPainter.Antialiasing)
        # painter.setCompositionMode(QPainter.CompositionMode_Plus)
        # painter.setCompositionMode(QPainter.CompositionMode_Screen)
        painter.setCompositionMode(QPainter.CompositionMode_HardLight)
        # painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)

        # setHeat callback also accesses heatpix
        with self.heatpixlock:
            painter.drawPixmap(QPoint(), self.heatpix)
        painter.end()

        self.label.setPixmap(dispix)


    @pyqtSlot(QPixmap)
    def setHeat(self, pixmap):
        # setImage callback also accesses heatpix
        with self.heatpixlock:
            self.heatpix = pixmap.copy()


    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.resize(self.width+2*self.leftmargin,self.height+2*self.topmargin)

        self.label = QLabel(self)
        self.label.move(self.leftmargin,self.topmargin)
        self.label.resize(self.width, self.height)

        self.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    myapp = ThermalPlayer()

    print("Video Thread")
    vthread = QThread()
    vthread.start()
    vth = VidThread()
    vth.width = myapp.width
    vth.height = myapp.height
    vth.changePixmap.connect(myapp.setImage)
    vth.moveToThread(vthread)
    vth.go.emit()

    print("MLX Thread")
    mlxthread = QThread()
    mlxthread.start()
    mlxt = MLXThread()
    mlxt.changeHeatmap.connect(myapp.setHeat)
    mlxt.moveToThread(mlxthread)
    mlxt.go.emit()

    sys.exit(app.exec_())
