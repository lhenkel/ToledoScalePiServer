#!/bin/sh

PROCESS_NUM=$(ps -ef | grep "pi_scale_server.py" | grep -v "grep" | wc -l)
# for degbuging...
$PROCESS_NUM
if [ $PROCESS_NUM -eq 1 ];
then
    echo 'Found'
else
    echo 'Not Found, starting scale'
    /usr/bin/python /jobs/piscale/pi_scale_server.py  > /jobs/piscale/scale.log 2>&1 &
fi

