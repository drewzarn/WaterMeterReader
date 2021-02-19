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
dbSelectCmd = """SELECT *
FROM ac_data
JOIN snapshots ON (
	snap_start_time BETWEEN ac_time and ac_end_time
	OR ac_time BETWEEN snap_start_time AND snap_end_time
	OR snap_end_time BETWEEN ac_time AND ac_end_time)
LEFT JOIN ac_interval_tests ON test_ac_time=ac_time
LEFT JOIN peak_test_cases ON case_id=test_case_id
WHERE test_ac_time IS NULL OR case_id IS NULL
ORDER BY ac_time ASC"""
dbTestInsertCmd = "INSERT INTO ac_interval_tests (test_ac_time, test_end_time, test_case_id, test_peak_times, test_peak_intervals, test_avg_interval, test_interval_stats, test_peak_count) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"

conf.CheckProc("Peak Tester")

testCases = {}
DBcursor.execute("SELECT * FROM peak_test_cases")
caseResults = DBcursor.fetchall()
for testCaseRow in caseResults:
    testCases[testCaseRow["case_id"]] = {"height": testCaseRow["case_peak_height"], "prominence": testCaseRow["case_peak_prominence"]}

while True:
    print("Beginning processing loop")

    DBcursor.execute(dbSelectCmd)
    dbResults = DBcursor.fetchall()

    print("{0} AC data blocks loaded".format(len(dbResults)))

    conf.CheckProc("Peak Tester")

    if len(dbResults) == 0:
        print("Waiting for data...")
        time.sleep(conf.AC_SAVE_WINDOW + 1)
    for acDataRow in dbResults:
        print("Processing {0}".format(acDataRow["ac_time"]))
        data = json.loads(acDataRow["ac_data"])

        for testCaseId in testCases:
            testCase = testCases[testCaseId]
            peakHeight = testCase["height"]
            peakProminence = testCase["prominence"]
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
                avgInterval = np.mean(peakIntervals)
                flowRate = conf.FLOW_PER_NUTATION * (60/avgInterval)
                if(stats.mode(peakIntervals)[0][0] > conf.PEAK_INTERVAL_MODE_THRESHOLD):
                    avgInterval = 0
                    flowRate = 0

#           peakTimes = np.float(peakTimes) if len(peakTimes) > 0 else np.empty([0], float)
#           peakIntervals = np.float(peakIntervals) if len(peakIntervals) > 0 else np.empty([0], float)
            
            DBcursor.execute(dbTestInsertCmd, (min(data['t']), max(data['t']), testCaseId, json.dumps(peakTimes.tolist()), json.dumps(peakIntervals), avgInterval, json.dumps(intervalStats), len(peakIntervals)))