import busio
import adafruit_mlx90393
import board
from statsmodels import api as sm
import matplotlib.pyplot as plt
import math
import numpy as np
import datetime
import time
import config as conf
print("Initializing...")

plt.style.use('seaborn-poster')

I2C_BUS = busio.I2C(board.SCL, board.SDA)
SENSOR = adafruit_mlx90393.MLX90393(I2C_BUS, gain=adafruit_mlx90393.GAIN_5X)

print("Collecting data")
while True:
    start = time.time()
    data = {"t": [], "raw": {"x": [], "y": [], "z": [], "s": []}, "ac": {"x": [], "y": [], "z": [], "s": []}}
    print("New snapshot starting")

    while time.time() - start < 3:
        MX, MY, MZ = SENSOR.magnetic
        MS = math.sqrt(MX*MX + MY*MY + MZ*MZ)
        data["t"].append(time.time() - start)
        data["raw"]["x"].append(MX)
        data["raw"]["y"].append(MY)
        data["raw"]["z"].append(MZ)
        data["raw"]["s"].append(MS)

        # Display the status field if an error occured, etc.
        if SENSOR.last_status > adafruit_mlx90393.STATUS_OK:
            SENSOR.display_status()

    np.save("/meterdata/{0}.raw".format(time.time()), data)

    print("Analyzing", len(data["t"]), "readings")

    xNorm = data["x"] - np.mean(data["x"])
    yNorm = data["y"] - np.mean(data["y"])
    zNorm = data["z"] - np.mean(data["z"])
    sNorm = data["s"] - np.mean(data["s"])

    # get the autocorrelation coefficient
    acX = sm.tsa.acf(xNorm, nlags=len(xNorm), fft=conf.AC_USE_FFT)
    acY = sm.tsa.acf(yNorm, nlags=len(yNorm), fft=conf.AC_USE_FFT)
    acZ = sm.tsa.acf(zNorm, nlags=len(zNorm), fft=conf.AC_USE_FFT)
    acS = sm.tsa.acf(sNorm, nlags=len(sNorm), fft=conf.AC_USE_FFT)

    print("Creating plots")

    fig = plt.figure(figsize=(9, 6))
    ax1 = fig.add_subplot(111)
    ax1.plot(data["t"], xNorm)
    ax1.set_xlabel(datetime.datetime.fromtimestamp(start).strftime('%H:%M:%S'))
    ax1.set_ylim(-max(abs(min(xNorm)), max(xNorm)),
                 max(abs(min(xNorm)), max(xNorm)))
    ax1.set_ylabel("Raw X")
    ax2 = ax1.twinx()
    ax2.set_ylim(-1, 1)
    ax2.set_ylabel("AC X", color="tab:red")
    ax2.plot(data["t"], acX, color="tab:red")
    plt.savefig("/var/www/html/x.png")
    fig.clear()
    plt.clf()

    #fig = plt.figure(figsize = (9, 6))
    ax1 = fig.add_subplot(111)
    ax1.plot(data["t"], yNorm)
    ax1.set_xlabel(datetime.datetime.fromtimestamp(start).strftime('%H:%M:%S'))
    ax1.set_ylim(-max(abs(min(yNorm)), max(yNorm)),
                 max(abs(min(yNorm)), max(yNorm)))
    ax1.set_ylabel("Raw Y")
    ax2 = ax1.twinx()
    ax2.set_ylim(-1, 1)
    ax2.set_ylabel("AC Y", color="tab:red")
    ax2.plot(data["t"], acY, color="tab:red")
    plt.savefig("/var/www/html/y.png")
    fig.clear()
    plt.clf()

    #fig = plt.figure(figsize = (9, 6))
    ax1 = fig.add_subplot(111)
    ax1.plot(data["t"], zNorm)
    ax1.set_xlabel(datetime.datetime.fromtimestamp(start).strftime('%H:%M:%S'))
    ax1.set_ylim(-max(abs(min(zNorm)), max(zNorm)),
                 max(abs(min(zNorm)), max(zNorm)))
    ax1.set_ylabel("Raw Z")
    ax2 = ax1.twinx()
    ax2.set_ylim(-1, 1)
    ax2.set_ylabel("AC Z", color="tab:red")
    ax2.plot(data["t"], acZ, color="tab:red")
    plt.savefig("/var/www/html/z.png")
    fig.clear()
    plt.clf()

    #fig = plt.figure(figsize = (9, 6))
    ax1 = fig.add_subplot(111)
    ax1.plot(data["t"], sNorm)
    ax1.set_xlabel(datetime.datetime.fromtimestamp(start).strftime('%H:%M:%S'))
    ax1.set_ylim(-max(abs(min(sNorm)), max(sNorm)),
                 max(abs(min(sNorm)), max(sNorm)))
    ax1.set_ylabel("Raw S")
    ax2 = ax1.twinx()
    ax2.set_ylim(-1, 1)
    ax2.set_ylabel("AC S", color="tab:red")
    ax2.plot(data["t"], acS, color="tab:red")
    plt.savefig("/var/www/html/s.png")
    fig.clear()
    plt.clf()

    fig.clear()
    plt.close('all')
