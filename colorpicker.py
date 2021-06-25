import cv2
import numpy as np
import sys

img = 'images/20210621-210216-base'
image_hsv = cv2.imread(img + '.png')
for p in range(0, 320, 20):
    pixel = image_hsv[p, 20]
    print(p, pixel)
