import cv2
import numpy as np
import math

img = np.zeros((320, 320, 3), np.uint8)

angle = 0
r = 100
while angle < 360:
    theta = np.radians(angle)
    x = r * math.cos(90 - theta) - 160
    y = r * math.sin(90 - theta) - 160
    g = math.floor(angle / 360 * 255)
    img[round(y)][round(x)] = [0, g, 255]
    print(angle, round(y), round(x))
    angle += 1

cv2.imwrite('circletest.png', img)