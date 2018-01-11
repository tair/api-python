#!/usr/bin/python
# file format:
# 4 columns for actionType, institutionName, startIp, endIp

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import IpRangeSerializer, PartySerializer
from party.models import IpRange, Party

# Begin main program:

# Open the source CSV file and load into memory.
IpRangeFilename = raw_input('Please enter a file name(*.csv) for ip range list:\n')

with open(IpRangeFilename, 'rb') as f:
    reader = csv.reader(f)
    IpRangeListData = list(reader)

# Processing Data
print 'Processing Data'

# count variable initialization
ipRangeExists = 0
partyCreated = 0
ipRangeLoaded = 0
ipRangeFailed = 0
cleared = []

for entry in IpRangeListData:
    actionType = entry[0]
    institutionName = entry[1]
    startIp = entry[2]
    endIp = entry[3]
    queryset = Party.objects.all().filter(partyType='organization')

    if actionType == 'create':
        partyId = None
        # when the party doesn't exist
        if not queryset.filter(name=institutionName).exists():
            #create party
            partySerializer = PartySerializer(data={'name':institutionName, 'partyType': 'organization'}, partial=True)
            if partySerializer.is_valid():
                partySerializer.save()
            else:
                print '[Party serializer invalid] ' + \
                      'type: ' + actionType + \
                      'institution: ' + institutionName + \
                      'start: ' + startIp + \
                      'end: ' + endIp
                ipRangeFailed += 1
                continue
            partyId = partySerializer.data['partyId']
            partyCreated += 1

        # when the party exists
        else:
            if queryset.filter(name=institutionName).count() > 1:
                print '[More than one party found with institution name] ' + \
                      'type: ' + actionType + \
                      'institution: ' + institutionName + \
                      'start: ' + startIp + \
                      'end: ' + endIp
                ipRangeFailed += 1
                continue
            partyId = queryset.filter(name=institutionName)[0].partyId
            ipRangeList = IpRange.objects.all().filter(partyId=partyId)
            nextIter = False
            for ipRange in ipRangeList:
                if ipRange.start == startIp and ipRange.end == endIp:
                    print '[Ip range already exists] ' + \
                          'type: ' + actionType + \
                          'institution: ' + institutionName + \
                          'start: ' + startIp + \
                          'end: ' + endIp
                    nextIter = True
                    ipRangeExists += 1
                    break
            if nextIter == True:
                continue
        # create ip range
        ipRangeSerializer = IpRangeSerializer(data={'start': startIp, 'end': endIp, 'partyId': partyId}, partial=True)
        if ipRangeSerializer.is_valid():
            ipRangeSerializer.save()
            ipRangeLoaded += 1
        else:
            print '[Ip range serializer invalid] ' + \
                  'type: ' + actionType + \
                  'institution: ' + institutionName + \
                  'start: ' + startIp + \
                  'end: ' + endIp
            ipRangeFailed += 1

    elif actionType == 'update':
        partyId = None
        # when the party doesn't exist
        if not queryset.filter(name=institutionName).exists():
            print '[Party does not exist] ' + \
                  'type: ' + actionType + \
                  'institution: ' + institutionName + \
                  'start: ' + startIp + \
                  'end: ' + endIp
            ipRangeFailed += 1
            continue

        # when the party exists
        elif queryset.filter(name=institutionName).count() > 1:
            print '[More than one party found with institution name] ' + \
                  'type: ' + actionType + \
                  'institution: ' + institutionName + \
                  'start: ' + startIp + \
                  'end: ' + endIp
            ipRangeFailed +=1
            continue
        else:
            partyId = queryset.filter(name=institutionName)[0].partyId
            if partyId not in cleared:
                IpRange.objects.all().filter(partyId=partyId).delete()
                cleared.append(partyId)

        # create ip range
        ipRangeSerializer = IpRangeSerializer(data={'start': startIp, 'end': endIp, 'partyId': partyId}, partial=True)
        if ipRangeSerializer.is_valid():
            ipRangeSerializer.save()
            ipRangeLoaded += 1
        else:
            print '[Ip range serializer invalid] ' + \
                  'type: ' + actionType + \
                  'institution: ' + institutionName + \
                  'start: ' + startIp + \
                  'end: ' + endIp
            ipRangeFailed += 1

print 'Loading Complete: ' + \
    'ipRangeLoaded: ' + str(ipRangeLoaded) + \
    'ipRangeExists: ' + str(ipRangeExists) + \
    'ipRangeFailed: ' + str(ipRangeFailed) + \
    'partyCreated: ' + str(partyCreated)
