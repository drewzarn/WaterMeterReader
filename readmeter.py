from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import os
import time
import dateutil.parser, socket

debug = 0 #0=none, 1=image and debug, 2=all steps
cropX = 160
cropY = 160
DIFFERENCE_THRESHOLD_PX = 25
RED_MIN = np.array([160, 40, 60], np.uint8)
RED_MAX = np.array([180, 80, 160], np.uint8)
GALLONS_PER_ANGLE = 10 / 360

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def auto_canny(image, sigma=0.33):
	# compute the median of the single channel pixel intensities
	v = np.median(image)
	# apply automatic Canny edge detection using the computed median
	lower = int(max(0, (1.0 - sigma) * v))
	upper = int(min(255, (1.0 + sigma) * v))
	edged = cv2.Canny(image, lower, upper)
	# return the edged image
	return edged

def output_image(image, prefix, filename, imgDebugLevel=3):
	if(debug >= imgDebugLevel):
		cv2.imwrite('images/' + str(prefix) + '-' + filename + '.png', image)

#History of readings so we can average them out and do things
readings = np.zeros((1, 2))
readings = readings[:0]

lastImg = None
log = open('log.txt', 'w')

# initialize the camera and grab a reference to the raw camera capture
with PiCamera() as camera:
	rawCapture = PiRGBArray(camera)
	time.sleep(1)

	while True:
		print('Capturing')
		captureTime = time.time()

		#Base image -  crop, HSV and mask
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		img = rawCapture.array
		output_image(img, captureTime, 'base', 1)
		#img = img[320 - cropY:320 + cropY, 340 - cropX:340 + cropX]

		#Diff the image with the last one to see if nothing moved
		if lastImg is None:
			lastImg = img.copy()
			continue
		else:
			imgDiff = cv2.cvtColor(cv2.absdiff(img, lastImg), cv2.COLOR_BGR2GRAY).astype(np.int16)
			imgDiff = (imgDiff - 5).clip(min=0)
			diffCount = cv2.countNonZero(imgDiff)
			if diffCount < DIFFERENCE_THRESHOLD_PX:
				if debug >= 2:
					log.write(str(captureTime) + ';' + 'nodifference;' + str(diffCount) + '\n')
				print('Insufficient difference (' + str(diffCount) + ') seen')
				lastImg = img.copy()
				time.sleep(1)
				continue
		lastImg = img.copy()

		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

		mask = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
		mask = cv2.medianBlur(mask, 5)
		output_image(mask, captureTime, 'mask', 2)

		debugimg = img.copy()

		#Find edges and circles
		edges = auto_canny(mask)
		edges = cv2.dilate(edges, np.ones((6,6)))
		edges = cv2.erode(edges, np.ones((3,3)))
		edges = cv2.blur(edges, (3,3))

		circles = cv2.HoughCircles(mask, cv2.HOUGH_GRADIENT, 5, 2, minRadius=60, maxRadius=100)

		if circles is not None:
			# convert the (x, y) coordinates and radius of the circles to integers
			circleAvg = np.average(circles[0], axis=0)
			circleAvg = np.round(circleAvg).astype("int")

			cv2.circle(debugimg, (circleAvg[0], circleAvg[1]),
					circleAvg[2], (0, 255, 0), 4)
			
			#Fill in the center circle on edges image
			cv2.circle(edges, (circleAvg[0], circleAvg[1]), circleAvg[2] + 15, (0, 0, 0), -1)
		output_image(edges, captureTime, 'edges', 2)
			
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

		if lines is None:
			output_image(debugimg, captureTime, 'debug', 0)
			continue
		else:
			#Clean up outlier lines
			lineMean = np.mean(lines, axis=0)
			lineStdDev = np.std(lines, axis=0)
			lineDistance = abs(lines - lineMean)
			maxDeviations = 2
			inlierFlags = lineDistance < maxDeviations * lineStdDev
			zipped = zip(lines, inlierFlags)
			inliers = []
			for lst, inlierMask in zipped:
				pairs = zip(lst, inlierMask)  # [(0, False), (1, False), (1, True), (1, True)]

				if inlierMask[0][0] and inlierMask[0][1]:
					inliers.append(lst)

			lines = np.array(inliers)
			lineAvg = np.average(lines, axis=0)

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

				angle = np.degrees(theta)

				#Figure out what octant the needle is in to set the angle correctly
				height, width = mask.shape[:2]
				maskedline = np.zeros((height, width, 3), np.uint8)
				cv2.line(maskedline, (x1, y1), (x2, y2), (255, 255, 255), 2)
				mask = cv2.dilate(mask, np.ones((3, 3)))
				maskedline = cv2.bitwise_and(maskedline, maskedline, mask=mask)
				maskedline = cv2.cvtColor(maskedline, cv2.COLOR_BGR2GRAY)
			
				leftCount = 0
				rightCount = 0
				for i in range(width):
					if maskedline[1, i] > 128 or maskedline[height - 1, i] > 128:
						if i < width / 2:
							leftCount += 1
						else:
							rightCount += 1
				for i in range(height):
					if maskedline[i, 1] > 128:
						leftCount += 1
					if maskedline[i, width - 1] > 128:
						rightCount += 1

				output_image(maskedline, captureTime, 'maskedline', 2)

				if(leftCount > rightCount):
					angle += 180

				cv2.line(debugimg, (x1, y1), (x2, y2), (255, 0, 0), 2)
				cv2.putText(debugimg, str(angle), (20, 300),
						cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

		output_image(debugimg, captureTime, 'debug', 1)
		readings = np.append(readings, np.array([[captureTime, angle]]), axis=0)
		log.write(str(captureTime) + ';angle;' + str(angle) + '\n')
		if(len(readings) > 5):
			readings = readings[len(readings) - 5:]
		if(len(readings) > 1):
			timeDelta = readings[len(readings) - 1][0] - readings[len(readings) - 2][0]
			angleDelta = readings[len(readings) - 1][1] - readings[len(readings) - 2][1]
			if(angleDelta < 0):
				readings = readings[:(len(readings) - 2)]
				continue
			usage = GALLONS_PER_ANGLE * angleDelta
			log.write(str(captureTime) + ';data;'+ str(angleDelta) + ';' + str(timeDelta) + ';' + str(usage) + '\n')
			print('{0}deg in {1}s ({2}) for {3} gal'.format(angleDelta, timeDelta, angleDelta / timeDelta, usage))

			socketStart = time.time()
			s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			s.connect(('172.24.84.122', 8080))
			message = str(captureTime)+' 62162 '+str(usage)+'\r\n'
			s.send(message.encode())
			print('Socket took ' + str(time.time() - socketStart))