#!/bin/bash

#if [[ $# -ne 2 ]] 
#then    
#    echo "Usage: ./runUnitTests -h '<hostname>' OR /runUnitTests --host '<hostname>'"
#    exit
#fi

export DJANGO_SETTINGS_MODULE=paywall2.settings


./manage.py runserver 172.31.34.88:8000 &
pid=$!

sleep 5

hasError=0

python -m metering.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

python -m subscription.pyTests $1 $2 
if [ $? != 0 ]
then
    hasError=1
fi

python -m authorization.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

python -m partner.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

pkill -TERM -P $pid

if [ $hasError == 1 ]
then
    exit 1
fi


