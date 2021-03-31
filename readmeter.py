from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import os
import time
from datetime import datetime
import dateutil.parser, socket
import threading, queue, math

debug = 0 #0=none, 1=image and debug, 2=all steps
cropX = 160
cropY = 160
DIFFERENCE_THRESHOLD_PX = 25
RED_MIN = np.array([160, 20, 60], np.uint8)
RED_MAX = np.array([180, 80, 160], np.uint8)
CHECK_RADIUS = 100
GALLONS_PER_ANGLE = 10 / 360

msgQueue = queue.Queue(0)

ANGLE_POINTS = {}
angle = 0
while angle < 360:
	theta = np.radians(angle)
	x = round(CHECK_RADIUS * math.cos(theta) - cropX)
	y = round(CHECK_RADIUS * math.sin(theta) - cropY)
	ANGLE_POINTS[angle] = [y, x]
	angle += 1

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

def send_emoncms(message):
	socketStart = time.time()
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect(('172.24.84.122', 8080))
	s.send(message.encode())
	#print('Socket took ' + str(time.time() - socketStart))

def ProcessMessageQueue():
	while True:
		if msgQueue.qsize() > 10:
			msgCount = 0
			msg = ""
			while msgCount < 10:
				msgCount += 1
				msg += msgQueue.get()
		else:
			msg = msgQueue.get()
		send_emoncms(msg)

#History of readings so we can average them out and do things
readings = np.zeros((1, 2))
readings = readings[:0]

lastImg = None
anglePrevious = None
angleCurrent = None
log = open('log.txt', 'w')

threading.Thread(target=ProcessMessageQueue, daemon=True).start()

# initialize the camera and grab a reference to the raw camera capture
with PiCamera() as camera:
	rawCapture = PiRGBArray(camera)
	time.sleep(1)

	while True:
		print('Capturing')
		captureTime = time.time()

		#Grab image and crop
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		img = rawCapture.array
		output_image(img, captureTime, 'base', 1)
		img = img[320 - cropY:320 + cropY, 340 - cropX:340 + cropX]

		if False:
			#Diff the image with the last one to see if nothing moved
			if lastImg is None:
				lastImg = img.copy()
				continue
			else:
				imgDiff = cv2.cvtColor(cv2.absdiff(img, lastImg), cv2.COLOR_BGR2GRAY).astype(np.int16)
				imgDiff = (imgDiff - 5).clip(min=0)
				diffCount = cv2.countNonZero(imgDiff)
				if diffCount < DIFFERENCE_THRESHOLD_PX:
					output_image(imgDiff, captureTime, 'diff-' + str(diffCount), 2)
					print('Insufficient difference (' + str(diffCount) + ') seen')
					msgQueue.put_nowait(str(captureTime)+' 62162 '+str(0)+'\r\n')
					lastImg = img.copy()
					time.sleep(1)
					continue
			lastImg = img.copy()

		#Convert to HSV and get mask
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		output_image(hsv_img, captureTime, 'hsv', 2)
		mask = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
		output_image(mask, captureTime, 'mask', 2)

		#Find the angle of the first white pixel
		for angle in reversed(sorted(ANGLE_POINTS.keys())):
			y, x = ANGLE_POINTS[angle]
			lastY, lastX = ANGLE_POINTS[0 if angle==359 else angle + 1]
			if mask[y, x] == 255 and mask[lastY, lastX] == 0:
				angleCurrent = angle
				break

		if debug == 2:
			cv2.putText(mask, str(angleCurrent), (120, 160),
						cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
			output_image(mask, captureTime, 'debug', 2)

		if anglePrevious is None:
			print('No previous angle')
			anglePrevious = angleCurrent
			continue

		msgQueue.put_nowait(str(captureTime)+' 12341 '+str(angleCurrent)+'\r\n')

		#Twent backwards. Nein!
		if angleCurrent < anglePrevious and abs(anglePrevious - angleCurrent) < 270:
			print(datetime.now().strftime("%H:%M:%S"), 'BACKWARDS!', angleCurrent, anglePrevious)
			msgQueue.put_nowait(str(captureTime)+' 62162 '+str(0)+'\r\n')
			continue

		angleDelta = angleCurrent - anglePrevious
		if(angleDelta < 0):
			angleDelta += 360
		print(datetime.now().strftime("%H:%M:%S"), 'Current: ', angleCurrent, "Previous", anglePrevious, "Delta", angleDelta)
		anglePrevious = angleCurrent

		if abs(angleDelta) > 270:
			print(datetime.now().strftime("%H:%M:%S"), 'Giant jump', angleCurrent, angleDelta)
			msgQueue.put_nowait(str(captureTime)+' 62162 '+str(0)+'\r\n')
			continue

		usage = GALLONS_PER_ANGLE * angleDelta
		print(datetime.now().strftime("%H:%M:%S"), angleCurrent, angleDelta, usage)

		msgQueue.put_nowait(str(captureTime)+' 62162 '+str(usage)+'\r\n')