#!/bin/bash

#if [[ $# -ne 2 ]] 
#then    
#    echo "Usage: ./runUnitTests -h '<hostname>' OR /runUnitTests --host '<hostname>'"
#    exit
#fi

export DJANGO_SETTINGS_MODULE=paywall2.settings


./manage.py runserver 172.31.34.88:8000 &
pid=$!

sleep 20

#python -m metering.pyTests $1 $2
python -m subscription.pyTests $1 $2 
python -m authorization.pyTests $1 $2

pkill -TERM -P $pid
