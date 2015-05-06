#!/bin/bash

#if [[ $# -ne 2 ]] 
#then    
#    echo "Usage: ./runUnitTests -h '<hostname>' OR /runUnitTests --host '<hostname>'"
#    exit
#fi

export DJANGO_SETTINGS_MODULE=paywall2.settings

#python -m metering.pyTests $1 $2
python -m subscription.pyTests $1 $2 
python -m authorization.pyTests $1 $2
