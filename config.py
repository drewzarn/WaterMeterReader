import numpy as np
import pymysql
np.set_printoptions(formatter={'float_kind':'{:f}'.format})

AXES = ["s", "x", "y", "z"]

DBHOST = "localhost"
DBUSER = "meterdb"
DBPASS = "meterpass"
DBNAME = "meters"

pymysql.converters.encoders[np.float64] = pymysql.converters.escape_float
pymysql.converters.conversions = pymysql.converters.encoders.copy()
pymysql.converters.conversions.update(pymysql.converters.decoders)
DB = pymysql.connect(DBHOST, DBUSER, DBPASS, DBNAME, autocommit=True)

CAPTURE_WINDOW_LENGTH = 10

AC_PROCESS_STEP = 1
AC_PROCESS_WINDOW = 3
AC_SAVE_WINDOW = 10
DETERMINANT_AXIS = "z"
AC_USE_FFT = True

PEAK_HEIGHT = 0.15
PEAK_PROMINENCE = 0.1
PEAK_INTERVAL_MODE_THRESHOLD = .15

FLOW_PER_NUTATION = 1/120

def CheckProc(procName):
    DBcursor = DB.cursor()
    dbProcCmd = "SELECT proc_run FROM processes WHERE proc_name='" + procName + "'"
    DBcursor.execute(dbProcCmd)
    procResult = DBcursor.fetchall()
    if procResult[0][0] == 0:
        print("Terminating " + procName)
        quit()
