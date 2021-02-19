#!/bin/bash

ROOT="/home/pi/meterreading/"
procs=("data-gatherer.py" "data-process.py" "data-findpeaks.py" "data-testpeaks.py")

while :; do
    for proc in ${procs[@]}; do
        RESULT=$(pgrep -f ${ROOT}${proc})
        if [ "${RESULT:-null}" = null ]; then
            echo "${proc} not running, starting "$proc
            $ROOT$proc &
        else
            echo "${proc} running"
        fi
    done
    sleep 10
done
