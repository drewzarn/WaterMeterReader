#!/usr/bin/env python3

print("Initializing...")
import config as conf
import numpy as np
import glob
import json
import pymysql
import os
from statsmodels import api as sm
import time

DBcursor = conf.DB.cursor(pymysql.cursors.DictCursor)
dbSelectCmd = "SELECT raw_time, raw_data FROM raw_data WHERE raw_status='new' ORDER BY raw_time ASC"
dbInsertCmd = "INSERT INTO ac_data (ac_time, ac_end_time, ac_data, ac_status) VALUES (%s, %s, %s, %s)"

conf.CheckProc("Data Processor")

while True:
    print("Beginning processing loop")
    timeArray = np.empty([0], float)
    dataArray = np.empty([0], float)
    acTimeArray = np.empty([0], float)
    acDataArray = np.empty([0], float)

    DBcursor.execute(dbSelectCmd)
    dbResults = DBcursor.fetchall()
    
    print("{0} raw data blocks loaded".format(len(dbResults)))

    if len(dbResults) == 0:
        print("Waiting for raw data...")
        time.sleep(conf.CAPTURE_WINDOW_LENGTH + 1)
        continue
    for rawDataRow in dbResults:
        print("Processing {0}".format(rawDataRow["raw_time"]))
        data = json.loads(rawDataRow["raw_data"])
        DBcursor.execute("UPDATE raw_data SET raw_status='processed' WHERE raw_time=%s", (rawDataRow["raw_time"], ))
        
        timeArray = np.concatenate([timeArray, np.array(data["t"])])
        timeDuration = max(timeArray) - min(timeArray)
        dataArray = np.concatenate([dataArray, np.array(data["raw"][conf.DETERMINANT_AXIS])])
        if(timeDuration > conf.AC_SAVE_WINDOW):
            break

    print("Data loaded for {0} seconds, {1} time samples, {2} data samples".format(timeDuration, len(timeArray), len(dataArray)))
    print("Time window: {0} - {1}".format(min(timeArray), max(timeArray)))

    #Normalize the data around 0
    dataArray = dataArray - np.mean(dataArray)

    #Step through the data and calculate autocorrelations
    while(len(timeArray) > 0):
        i = 0
        stepI = 0
        while(timeArray[i] - timeArray[0] < conf.AC_PROCESS_WINDOW):
            if(timeArray[i] - timeArray[0] < conf.AC_PROCESS_STEP):
                stepI = i + 1
            i += 1
            if(i == len(timeArray)):
                i -= 1
                break

        if(timeArray[i] - timeArray[0] < conf.AC_PROCESS_WINDOW):
            print("Skipping processing; insufficent data to fill window")
            break

        print("Working {0} second window of {1} samples".format(timeArray[i] - timeArray[0], i))
        workingData = dataArray[:i]
        acWindow = sm.tsa.acf(workingData, nlags=len(workingData), fft=conf.AC_USE_FFT)
        if(len(acDataArray) == 0):
            acWindow[0] = acWindow[1]
        else:
            acWindow = np.delete(acWindow, 0)

        acI = 0
        while(acI < stepI):
            acTimeArray = np.append(acTimeArray, timeArray[min(acI, len(timeArray) - 1)])
            acDataArray = np.append(acDataArray, acWindow[min(acI, len(acWindow) - 1)])
            acI += 1

        timeArray = timeArray[stepI:]
        dataArray = dataArray[stepI:]
    acData = {"t": acTimeArray.tolist(), "d": acDataArray.tolist()}
    jData = json.dumps(acData)
    DBcursor.execute(dbInsertCmd, (min(acTimeArray), max(acTimeArray), jData, "new"))

    conf.CheckProc("Data Processor")