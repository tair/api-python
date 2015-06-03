#!/bin/bash

#if [[ $# -ne 2 ]] 
#then    
#    echo "Usage: ./runUnitTests -h '<hostname>' '<internalip:port>' OR /runUnitTests --host '<hostname>' '<internalip:port>'"
#    exit
#fi

export DJANGO_SETTINGS_MODULE=paywall2.settings


./manage.py runserver $3 &
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

python -m party.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

python -m loggingapp.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

python -m apikey.pyTests $1 $2
if [ $? != 0 ]
then
    hasError=1
fi

pkill -TERM -P $pid

if [ $hasError == 1 ]
then
    exit 1
fi
