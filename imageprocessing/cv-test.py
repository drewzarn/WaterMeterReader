# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import os
import time


def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged


for filename in os.listdir('.'):
	if not filename.endswith('090.png'):
		continue

	#Base image -  crop, HSV and mask
	img = cv2.imread(filename)
	cropX = 160
	cropY = 160
	img = img[320 - cropY:320 + cropY, 340 - cropX:340 + cropX]

	hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

	RED_MIN = np.array([160, 40, 60], np.uint8)
	RED_MAX = np.array([180, 80, 160], np.uint8)

	mask = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
	mask = cv2.medianBlur(mask, 5)

	debugimg = img.copy()

	#Find edges and circles
	edges = auto_canny(mask)
	edges = cv2.blur(edges, (3,3))

	circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT,
							   5, 2, minRadius=60, maxRadius=100)
		
	if circles is not None:
		# convert the (x, y) coordinates and radius of the circles to integers
		circleAvg = np.average(circles[0], axis=0)
		circleAvg = np.round(circleAvg).astype("int")

		cv2.circle(debugimg, (circleAvg[0], circleAvg[1]),
				   circleAvg[2], (0, 255, 0), 4)
		
		#Fill in the center circle edges
		cv2.circle(edges, (circleAvg[0], circleAvg[1]),
				   circleAvg[2] + 15, (0, 0, 0), -1)
	
	cv2.imwrite(filename.replace('.png', '-edges.png'), edges)

	#Find lines
	lineThreshold = 150
	lines = cv2.HoughLines(edges, 2, np.pi/180, lineThreshold)
	#If there aren't enough lines, drop the threshold and keep trying
	while(lines is None or (len(lines) < 4 and lineThreshold > 40)):
		lineThreshold = lineThreshold - 5
		lines = cv2.HoughLines(edges, 2, np.pi/180, lineThreshold)
		if lines is None:
			continue
		line = lines[len(lines) - 1]
		for rho, theta in line:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))

			cv2.line(debugimg, (x1, y1), (x2, y2), (0, 0, 255), 2)
		
	if lines is not None:
		lineAvg = np.average(lines, axis=0)
		#If odd number of lines, average the ones above and below the average to even them out
		if(len(lines) > 1 and len(lines) % 2 == 1):
			lineAvg = lineAvg[0]
			flatLines = lines[:, 0, :]
			above = np.array([np.zeros(2)])
			below = np.array([np.zeros(2)])
			for line in flatLines:
				if line[0] > lineAvg[0]:
					above = np.append(above, [line], axis=0)
				else:
					below = np.append(below, [line], axis=0)
			above = np.delete(above, 0, axis=0)
			below = np.delete(below, 0, axis=0)
			above = np.average(above, axis=0)
			below = np.average(below, axis=0)
			lineAvg = [np.array(below + above)/2]

		#Get points for the average line
		for rho, theta in lineAvg:
			a = np.cos(theta)
			b = np.sin(theta)
			x0 = a*rho
			y0 = b*rho
			x1 = int(x0 + 1000*(-b))
			y1 = int(y0 + 1000*(a))
			x2 = int(x0 - 1000*(-b))
			y2 = int(y0 - 1000*(a))

		#Get the angle for the line
		angle = np.degrees(np.arctan(abs(y2 - y1) / abs(x2 - x1)))
		cv2.putText(debugimg, str(angle), (20, 30),
					cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
		cv2.line(debugimg, (x1, y1), (x2, y2), (255, 0, 0), 2)

		#Figure out what octent the needle is in to set the angle correctly
		#?????

		#Draw the component lines for debug		
		for line in lines:
			for rho, theta in line:
				a = np.cos(theta)
				b = np.sin(theta)
				x0 = a*rho
				y0 = b*rho
				x1 = int(x0 + 1000*(-b))
				y1 = int(y0 + 1000*(a))
				x2 = int(x0 - 1000*(-b))
				y2 = int(y0 - 1000*(a))

				cv2.line(debugimg, (x1, y1), (x2, y2), (0, 0, 255), 2)

	cv2.imwrite(filename.replace('.png', '-debug.png'), debugimg)
