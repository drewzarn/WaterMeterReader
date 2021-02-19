#!/usr/bin/env python3

print("Initializing...")
import config as conf
import time
import json
import math
import board
import adafruit_mlx90393
import busio

I2C_BUS = busio.I2C(board.SCL, board.SDA)
SENSOR = adafruit_mlx90393.MLX90393(I2C_BUS, gain=adafruit_mlx90393.GAIN_5X)

DBcursor = conf.DB.cursor()
dbInsertCmd = "INSERT INTO raw_data (raw_time, raw_data, raw_status) VALUES (%s, %s, %s)"
conf.CheckProc("Data Gatherer")

print("Collecting data")
while True:
    start = time.time()
    data = {"t": [], "raw": {"x": [], "y": [], "z": [], "s": []}}
    print("New snapshot starting")

    while time.time() - start < conf.CAPTURE_WINDOW_LENGTH:
        MX, MY, MZ = SENSOR.magnetic
        MS = math.sqrt(MX*MX + MY*MY + MZ*MZ)
        data["t"].append(time.time())
        data["raw"]["x"].append(MX)
        data["raw"]["y"].append(MY)
        data["raw"]["z"].append(MZ)
        data["raw"]["s"].append(MS)
        
        # Display the status field if an error occured, etc.
        if SENSOR.last_status > adafruit_mlx90393.STATUS_OK:
            SENSOR.display_status()

    jsonData = json.dumps(data)
    DBcursor.execute(dbInsertCmd, (min(data["t"]), jsonData, "new"))

    conf.CheckProc("Data Gatherer")