#!/usr/bin/env python3

import matplotlib.pyplot as plt
import time
from scipy import stats
from scipy.signal import find_peaks
import os
import pymysql
import json
import numpy as np
import glob
import config as conf
print("Initializing...")

DBcursor = conf.DB.cursor(pymysql.cursors.DictCursor)
dbSelectCmd = "SELECT ac_time, ac_data FROM ac_data WHERE ac_status='new' ORDER BY ac_time ASC"
dbInsertCmd = "INSERT INTO interval_data (int_time, int_interval, int_duration, int_stats) VALUES (%s, %s, %s, %s)"

conf.CheckProc("Peak Finder")

while True:
    print("Beginning processing loop")

    DBcursor.execute(dbSelectCmd)
    dbResults = DBcursor.fetchall()

    print("{0} AC data blocks loaded".format(len(dbResults)))

    conf.CheckProc("Peak Finder")

    if len(dbResults) == 0:
        print("Waiting for data...")
        time.sleep(conf.AC_SAVE_WINDOW + 1)
    for acDataRow in dbResults:
        print("Processing {0}".format(acDataRow["ac_time"]))
        data = json.loads(acDataRow["ac_data"])
        DBcursor.execute("UPDATE ac_data SET ac_status='processed' WHERE ac_time=%s", (acDataRow["ac_time"], ))

        peakHeight = conf.PEAK_HEIGHT
        peakProminence = conf.PEAK_PROMINENCE
        peaks, _ = find_peaks(
            data["d"], height=peakHeight, prominence=peakProminence)
        peakTimes = np.empty([0])
        for peakI in peaks:
            peakTimes = np.append(peakTimes, data["t"][peakI])

        pi = 1
        peakIntervals = []
        while pi < len(peakTimes):
            peakIntervals.append(peakTimes[pi] - peakTimes[pi - 1])
            pi += 1
        avgInterval = 0
        flowRate = 0
        intervalStats = {"min": 0, "max": 0,
                        "mean": 0, "stddev": 0, "variation": 0}
        if(len(peakIntervals) > 0):
            intervalStats = {"min": min(peakIntervals), "max": max(peakIntervals), "mean": np.mean(
                peakIntervals), "stddev": stats.tstd(peakIntervals), "variation": stats.variation(peakIntervals)}
            print(intervalStats)
            avgInterval = np.mean(peakIntervals)
            flowRate = conf.FLOW_PER_NUTATION * (60/avgInterval)
            if(stats.mode(peakIntervals)[0][0] > conf.PEAK_INTERVAL_MODE_THRESHOLD):
                avgInterval = 0
                flowRate = 0

            DBcursor.execute(dbInsertCmd, (min(data['t']), avgInterval, max(data['t']) - min(data['t']), json.dumps(intervalStats)))