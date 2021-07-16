from picamera.array import PiRGBArray
from picamera import PiCamera
import cv2
import numpy as np
import os
import time
from datetime import datetime
import dateutil.parser, socket
import threading, queue, math, json
import paho.mqtt.client as mqtt

mqttSettings = {"server": "homeassistant.kline", "port": 1883, "user": "watermeter", "password": "watermeter", "keepalive": 60, "topicBase": "watermeter"}
mqttClient = mqtt.Client(mqttSettings["user"])
mqttClient.connect(mqttSettings["server"], mqttSettings["port"], mqttSettings["keepalive"])
mqttClient.publish(mqttSettings["topicBase"] + "/status", "starting")

debug = 0 #0=none, 1=image and debug, 2=all steps
cropX = 160
cropY = 160
needleCenterX = 300
needleCenterY = 330
RED_MIN = np.array([0, 0, 0], np.uint8)
RED_MAX = np.array([50, 255, 255], np.uint8)
CHECK_RADIUS = 100
GALLONS_PER_DEGREE = 10 / 360

msgQueue = queue.Queue(0)

intervalUsageBase = {15: 0, 60: 0, 3600: 0}
mqttData = {
	'time': 0,
	'usage': 0,
	'angle': 0,
	'averageLevel': 0,
	'intervalUsages': intervalUsageBase.copy(),
	'message': None,
	'queuesize': 0
}

usageByTime = {}
maxUsageInterval = max(intervalUsageBase)

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

def ProcessMessageQueue():
	while True:
		msg = msgQueue.get()
		mqttClient.publish(mqttSettings["topicBase"] + "/data", json.dumps(msg))

def QueueMessage(data):
	data['queuesize'] = msgQueue.qsize()
	msgQueue.put_nowait(data)

angleCurrent = None
anglePrevious = None
anglePrevious2 = None
anglePrevious3 = None
captureTime = None

threading.Thread(target=ProcessMessageQueue, daemon=True).start()

# initialize the camera and grab a reference to the raw camera capture
with PiCamera() as camera:
	rawCapture = PiRGBArray(camera)
	time.sleep(1)

	while True:
		#Make it run approx every 5s
		if(captureTime is not None and anglePrevious3 is not None):
			sleepTime = 5.0 - (time.time() - captureTime)
			time.sleep(sleepTime if sleepTime > 0 else 0)

		captureTime = time.time()
		captureTimeFriendly = datetime.now().strftime("%Y%m%d-%H%M%S")

		#Reset fields that need it
		mqttData['time'] = captureTime
		mqttData['message'] = None
		mqttData['usage'] = 0
		mqttData['intervalUsages'] = intervalUsageBase.copy()

		#Grab image and crop
		rawCapture = PiRGBArray(camera)
		camera.capture(rawCapture, format="bgr")
		img = rawCapture.array
		img = img[needleCenterY - cropY:needleCenterY + cropY, needleCenterX - cropX:needleCenterX + cropX]
		output_image(img, captureTimeFriendly, 'base', 2)

		mqttData['averageLevel'] = np.mean(np.mean(img, axis=2))
		
		#Convert to HSV and get mask
		hsv_img = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
		output_image(hsv_img, captureTimeFriendly, 'hsv', 2)
		mask = cv2.inRange(hsv_img, RED_MIN, RED_MAX)
		output_image(mask, captureTimeFriendly, 'mask', 2)

		#MedianBlur
		blur_mask = cv2.medianBlur(mask, 3)
		output_image(blur_mask, captureTimeFriendly, 'blurmask', 2)

		workingImg = blur_mask

		#Find the angle of the first white pixel
		debugImg = cv2.cvtColor(workingImg, cv2.COLOR_GRAY2RGB)
		for angle in reversed(sorted(ANGLE_POINTS.keys())):
			y, x = ANGLE_POINTS[angle]
			lastY, lastX = ANGLE_POINTS[0 if angle==359 else angle + 1]
			debugImg[y, x] = (0, 255, 0) if workingImg[y, x] == 255 else (0, 0, 255)
			if workingImg[y, x] == 255 and workingImg[lastY, lastX] == 0:
				angleCurrent = angle
				break

		mqttData['angle'] = angleCurrent

		if debug == 2:
			cv2.putText(debugImg, str(angleCurrent), (120, 160), cv2.FONT_HERSHEY_SIMPLEX, 1, 0, 2)
			output_image(debugImg, captureTimeFriendly, 'debug', 2)

		if anglePrevious is None or anglePrevious2 is None or anglePrevious3 is None:
			anglePrevious3 = anglePrevious2
			anglePrevious2 = anglePrevious
			anglePrevious = angleCurrent
			continue

		#Twent backwards. Nein!
		if mqttData['message'] is None and angleCurrent < anglePrevious and abs(anglePrevious - angleCurrent) < 270:
			print(datetime.now().strftime("%H:%M:%S"), 'BACKWARDS! from', anglePrevious, 'to', angleCurrent)
			mqttData['usage'] = 0
			mqttData['message'] = 'Backwards'

		angleDelta = angleCurrent - anglePrevious
		if(angleDelta < 0):
			angleDelta += 360
		anglePrevious3 = anglePrevious2
		anglePrevious2 = anglePrevious
		anglePrevious = angleCurrent
		
		#Make sure angle is consistent
		if mqttData['message'] is None and (anglePrevious < anglePrevious2 or anglePrevious < anglePrevious3):
			mqttData['usage'] = 0
			mqttData['message'] = 'Inconsistent readings ' + str(anglePrevious) + ', ' + str(anglePrevious2) + ', ' + str(anglePrevious3)

		if mqttData['message'] is None and abs(angleDelta) > 90:
			mqttData['usage'] = 0
			mqttData['message'] = 'Angle jump of ' + str(angleDelta)

		if mqttData['message'] is None:
			mqttData['usage'] = GALLONS_PER_DEGREE * angleDelta

		#Get usage over intervals
		usageByTime[captureTime] = mqttData['usage']
		intervalUsages = intervalUsageBase.copy()
		for interval, intervalUsage in list(intervalUsages.items()):
			for k,v in list(usageByTime.items()):
				if(captureTime - k > maxUsageInterval):
					del usageByTime[k]
					continue
				if(captureTime - k <= interval):
					intervalUsages[interval] += usageByTime[k]

		mqttData['intervalUsages'] = intervalUsages
		QueueMessage(mqttData)
