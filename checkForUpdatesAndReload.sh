#!/bin/sh
ps aux | grep pi_scale_server | grep -v "grep" | awk  '{print $2}' | xargs kill -9

/usr/bin/python /jobs/piscale/pi_scale_server.py  > /jobs/piscale/scale.log 2>&1 &
