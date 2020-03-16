"""
Image capture using Adafruit MLX90640 thermal camera.
class provides the structure needed to run the MLX reader
in its own thread. The captured frame is forwarded to a receiver
using the Signal/Slot mechanism. The utility functions and
heatmap coefficients come from Adafruit's example code.

Author: skip.tavakkolian@gmail.com
"""

import os
import math
import time
import board
import busio

from PIL import Image
from PIL.ImageQt import ImageQt
import cv2
import sys
from PyQt5.QtWidgets import  QWidget, QLabel, QApplication
from PyQt5.QtCore import QObject, QThread, Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

import adafruit_mlx90640

#some utility functions
def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def gaussian(x, a, b, c, d=0):
    return a * math.exp(-(x - b)**2 / (2 * c**2)) + d

def gradient(x, width, cmap, spread=1):
    width = float(width)
    r = sum([gaussian(x, p[1][0], p[0] * width, width/(spread*len(cmap))) for p in cmap])
    g = sum([gaussian(x, p[1][1], p[0] * width, width/(spread*len(cmap))) for p in cmap])
    b = sum([gaussian(x, p[1][2], p[0] * width, width/(spread*len(cmap))) for p in cmap])
    r = int(constrain(r*255, 0, 255))
    g = int(constrain(g*255, 0, 255))
    b = int(constrain(b*255, 0, 255))
    return r, g, b

class MLXThread(QObject):
    #low range of the sensor (this will be black on the screen)
    MINTEMP = 20.
    #high range of the sensor (this will be white on the screen)
    MAXTEMP = 50.
    #how many color values we can have
    COLORDEPTH = 1000
    heatmap = (
        (0.0, (0, 0, 0)),
        (0.20, (0, 0, .5)),
        (0.40, (0, .5, 0)),
        (0.60, (.5, 0, 0)),
        (0.80, (.75, .75, 0)),
        (0.90, (1.0, .75, 0)),
        (1.00, (1.0, 1.0, 1.0)),
    )
    changeHeatmap = pyqtSignal(QPixmap)
    go = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.go.connect(self.run)

    @pyqtSlot()
    def run(self):
        print("MLXThread")
        colormap = [0] * self.COLORDEPTH
        for i in range(self.COLORDEPTH):
            colormap[i] = gradient(i, self.COLORDEPTH, self.heatmap)

        i2c = busio.I2C(board.SCL, board.SDA)
        mlx = adafruit_mlx90640.MLX90640(i2c)
        mlx.refresh_rate = adafruit_mlx90640.RefreshRate.REFRESH_8_HZ
        frame = [0] * 768

        while True:
            # stamp = time.monotonic()
            try:
                mlx.getFrame(frame)
            except ValueError:
                print("ValueError")
                continue        # these happen, no biggie - retry

            # print("Read 2 frames in %0.2f s" % (time.monotonic()-stamp))

            pixels = [0] * 768
            for i, pixel in enumerate(frame):
                coloridx = map_value(pixel, self.MINTEMP, self.MAXTEMP, 0, self.COLORDEPTH - 1)
                coloridx = int(constrain(coloridx, 0, self.COLORDEPTH-1))
                pixels[i] = colormap[coloridx]

            img = Image.new('RGB', (32,24))
            img.putdata(pixels)
            img = img.resize((640, 480), Image.BICUBIC)
            img = ImageQt(img)
            pixmap = QPixmap.fromImage(img)
            self.changeHeatmap.emit(pixmap)

