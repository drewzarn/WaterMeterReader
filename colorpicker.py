import cv2
import numpy as np
import sys

image_hsv = cv2.imread('images/1617157441.1182852-hsv.png')
pixel = image_hsv[115, 115]
print(pixel)