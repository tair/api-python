#!/usr/bin/python
# this file is used for the case of non-NSTL bulk load and might have issues.
# file format:
# columns for actionType, institutionName, startIp, endIp, countryId(127 for China), consortiumId(31772 for NSTL)

import django
import os
import csv
import sys
import re
from django.core.exceptions import ValidationError
from netaddr.core import AddrFormatError
from django.db.utils import IntegrityError
from collections import defaultdict
from netaddr import IPAddress

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import IpRangeSerializer, PartySerializer
from party.models import IpRange, Party, PartyAffiliation, Country

# Begin main program:

# Open the source CSV file and load into memory.
IpRangeFilename = sys.argv[1]

with open(IpRangeFilename, 'rU') as f:
    reader = csv.reader(f)
    IpRangeListData = list(reader)

errlog = open("ipLoadingErrorLog.csv", "w+")
# Processing Data
print 'Processing Data'

# count variable initialization
ipRangeExists = 0
partyCreated = 0
ipRangeLoaded = 0
ipRangeError = 0
cleared = []

potentialExistingParty = defaultdict(set)

queryset = Party.objects.all().filter(partyType='organization')

for entry in IpRangeListData:
    try:
        actionType = entry[0]
        institutionName = entry[1]
        startIp = entry[2]
        endIp = entry[3]
        countryId = entry[4]
        consortiumId = entry[5]
        print institutionName
        print len(list(Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")")))
        # remove any blance spaces or non-ascii charactors from the ip ranges
        # whitelist = set('abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.:')
        # startIp = ''.join(filter(whitelist.__contains__, startIp))
        # endIp = ''.join(filter(whitelist.__contains__, endIp))
        startIp.replace(" ", "")
        endIp.replace(" ", "")
        startIp.strip()
        endIp.strip()

        # create ip range from '-' format e.g. 1.2.3.0-255 ==> start: 1.2.3.0 end: 1.2.3.255
        if '-' in startIp:
            if endIp:
                errlog.write("Error institution: " + institutionName + " invalid ip: " + startIp + " " + endIp + '\n')
                continue
            if len(startIp.split('-')) != 2:
                errlog.write("Error institution: " + institutionName + " invalid starting ip: " + startIp + '\n')
                continue
            # errlog.write("Warning institution: " + institutionName + " reconstructed ip: " + startIp + " " + endIp + '\n')
            s, e = startIp.split('-')
            startIp = s
            l = s.split('.')[:3]
            l.append(e)
            endIp = '.'.join(l)

        # empty startIp or endIp
        if not startIp:
            startIp = endIp
            # errlog.write("Warning institution: " + institutionName + " copied starting ip: " + startIp + '\n')
        if not endIp:
            endIp = startIp
            # errlog.write("Warning institution: " + institutionName + " copied ending ip: " + endIp + '\n')

        if not re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").match(startIp):
            errlog.write("Error institution: " + institutionName + " not ipv4 format: " + startIp  + '\n')
            continue

        if not re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").match(endIp):
            errlog.write("Error institution: " + institutionName + " not ipv4 format: " + endIp  + '\n')
            continue

        # remove leading 0
        if len(startIp.split('.')) == 4:
            startIpList = startIp.split('.')
            for i in xrange(len(startIpList)):
                while startIpList[i].startswith('0') and startIpList[i] != '0':
                    startIpList[i] = startIpList[i][1:]
            startIp = '.'.join(startIpList)

        if len(endIp.split('.')) == 4:
            endIpList = endIp.split('.')
            for i in xrange(len(endIpList)):
                while endIpList[i].startswith('0') and endIpList[i] != '0':
                    endIpList[i] = endIpList[i][1:]
            endIp = '.'.join(endIpList)

        try:
            if len(list(Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")")))==0:
                if IpRange.objects.all().filter(start=startIp).exists() or IpRange.objects.all().filter(end=endIp).exists():
                    potentialExistingParty[institutionName].update(IpRange.objects.all().filter(start=startIp).values_list('partyId', flat=True))
                    potentialExistingParty[institutionName].update(IpRange.objects.all().filter(end=endIp).values_list('partyId', flat=True))
                    # fw.write('Party could be in database: ' + institutionName + '\n')
                    continue
        except Exception as e:
            errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp)
            errlog.write(str(e) + '\n')
            raise Exception(str(e))

    except (ValidationError, AddrFormatError, IntegrityError, UnicodeDecodeError) as e:
        errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp + '\n')
        errlog.write(str(e) + '\n')
        continue

for k,v in potentialExistingParty.iteritems():
    s = ','.join([str(n) for n in v])
    errlog.write("Could be in database: "+ ',' + k + ',' + s + '\n')

#sys.exit()

for entry in IpRangeListData:
    try:
        actionType = entry[0]
        institutionName = entry[1]
        startIp = entry[2]
        endIp = entry[3]
        countryId = entry[4]
        consortiumId = entry[5]

        # remove any blance spaces or non-ascii charactors from the ip ranges
        # whitelist = set('abcdefghijklmnopqrstuvwxyABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890.:')
        # startIp = ''.join(filter(whitelist.__contains__, startIp))
        # endIp = ''.join(filter(whitelist.__contains__, endIp))
        startIp.replace(" ", "")
        endIp.replace(" ", "")
        startIp.strip()
        endIp.strip()

        # create ip range from '-' format e.g. 1.2.3.0-255 ==> start: 1.2.3.0 end: 1.2.3.255
        if '-' in startIp:
            if endIp:
                errlog.write("Error institution: " + institutionName + " invalid ip: " + startIp + " " + endIp + '\n')
                continue
            if len(startIp.split('-')) != 2:
                errlog.write("Error institution: " + institutionName + " invalid starting ip: " + startIp + '\n')
                continue
            # errlog.write("Warning institution: " + institutionName + " reconstructed ip: " + startIp + " " + endIp + '\n')
            s, e = startIp.split('-')
            startIp = s
            l = s.split('.')[:3]
            l.append(e)
            endIp = '.'.join(l)

        # for empty startIp or endIp
        if not startIp:
            startIp = endIp
            # errlog.write("Warning institution: " + institutionName + " copied starting ip: " + startIp + '\n')
        if not endIp:
            endIp = startIp
            # errlog.write("Warning institution: " + institutionName + " copied ending ip: " + endIp + '\n')

        # remove leading 0
        if len(startIp.split('.')) == 4:
            startIpList = startIp.split('.')
            for i in xrange(len(startIpList)):
                while startIpList[i].startswith('0') and startIpList[i] != '0':
                    startIpList[i] = startIpList[i][1:]
            startIp = '.'.join(startIpList)

        if len(endIp.split('.')) == 4:
            endIpList = endIp.split('.')
            for i in xrange(len(endIpList)):
                while endIpList[i].startswith('0') and endIpList[i] != '0':
                    endIpList[i] = endIpList[i][1:]
            endIp = '.'.join(endIpList)


        if len(list(Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")"))) == 0:
            if institutionName in potentialExistingParty:
                # errlog.write('Party could be in database: ' + institutionName + '\n')
                continue

        print 'Processing: ' + institutionName

        if actionType == 'create':
            partyId = None
            # when the party doesn't exist
            if len(list(Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")")))==0:
                # create party
                if not Country.objects.all().filter(countryId=countryId):
                    raise Exception('[Country Not Found] ' + countryId)
                elif Country.objects.all().filter(countryId=countryId).count() > 1:
                    raise Exception('[More than one record found with country id] ' + countryId)
                else:
                    partySerializer = PartySerializer(
                        data={'name': institutionName, 'partyType': 'organization', 'country': countryId}, partial=True)
                if partySerializer.is_valid():
                    partySerializer.save()
                    print '[New Party Created] ' + institutionName
                else:
                    raise Exception('[Party serializer invalid] ' + \
                                    'type: ' + actionType + \
                                    'institution: ' + institutionName + \
                                    'start: ' + startIp + \
                                    'end: ' + endIp)
                if consortiumId:
                    partyId = partySerializer.data['partyId']
                    childParty = Party.objects.get(partyId=partyId)
                    parentParty = Party.objects.get(partyId=consortiumId)
                    PartyAffiliation.objects.create(childPartyId=childParty, parentPartyId=parentParty)
                    print '[PartyAffiliation Created] ' + \
                          'institution: ' + institutionName + \
                          'consortium: ' + parentParty.name
                partyCreated += 1

            # when the party exists
            else:
                if len(list(Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")")))>1:
                    raise Exception('[More than one party found with institution name] ' + \
                                    ' type: ' + actionType + \
                                    ' institution: ' + institutionName + \
                                    ' start: ' + startIp + \
                                    ' end: ' + endIp + \
                                    ' parties: ' + ','.join([str(int(p.partyId)) for p in Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\""+institutionName+"\")")]))
                partyId = Party.objects.raw("SELECT partyId FROM Party WHERE partyType=\"organization\" AND UPPER(name) = UPPER(\"" + institutionName + "\")")[0].partyId
                if consortiumId:
                    childParty = Party.objects.get(partyId=partyId)
                    parentParty = Party.objects.get(partyId=consortiumId)
                    party, created = PartyAffiliation.objects.get_or_create(childPartyId=childParty, parentPartyId=parentParty)
                    if created:
                        print '[PartyAffiliation Created] ' + \
                              'institution: ' + institutionName + \
                              'consortium: ' + parentParty.name
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
                print '[IpRange Created] ' + \
                      'type: ' + actionType + \
                      'institution: ' + institutionName + \
                      'start: ' + startIp + \
                      'end: ' + endIp
                ipRangeLoaded += 1
            else:
                raise Exception('[Ip range serializer invalid] ' + \
                                'type: ' + actionType + \
                                'institution: ' + institutionName + \
                                'start: ' + startIp + \
                                'end: ' + endIp)

        elif actionType == 'update':
            partyId = None
            # when the party doesn't exist
            if not queryset.filter(name=institutionName).exists():
                raise Exception('[Party does not exist] ' + \
                                'type: ' + actionType + \
                                'institution: ' + institutionName + \
                                'start: ' + startIp + \
                                'end: ' + endIp)

            # when the party exists
            elif queryset.filter(name=institutionName).count() > 1:
                raise Exception('[More than one party found with institution name] ' + \
                                'type: ' + actionType + \
                                'institution: ' + institutionName + \
                                'start: ' + startIp + \
                                'end: ' + endIp)
            else:
                partyId = queryset.filter(name=institutionName)[0].partyId
                if partyId not in cleared:
                    IpRange.objects.all().filter(partyId=partyId).delete()
                    cleared.append(partyId)

            # create ip range
            ipRangeSerializer = IpRangeSerializer(data={'start': startIp, 'end': endIp, 'partyId': partyId}, partial=True)
            if ipRangeSerializer.is_valid():
                ipRangeSerializer.save()
                print '[IpRange Created] ' + \
                      'type: ' + actionType + \
                      'institution: ' + institutionName + \
                      'start: ' + startIp + \
                      'end: ' + endIp
                ipRangeLoaded += 1
            else:
                raise Exception('[Ip range serializer invalid] ' + \
                                'type: ' + actionType + \
                                'institution: ' + institutionName + \
                                'start: ' + startIp + \
                                'end: ' + endIp)
    # except (ValidationError, AddrFormatError, IntegrityError, UnicodeDecodeError) as e:
    except Exception as e:
        ipRangeError += 1
        print '[IpRange Error] ' + \
              'type: ' + actionType + \
              'institution: ' + institutionName + \
              'start: ' + startIp + \
              'end: ' + endIp
        errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp + ' ')
        errlog.write(str(e) + '\n')
        continue
errlog.close()
print 'Loading Complete: ' + '\n' + \
      'ipRangeLoaded: ' + str(ipRangeLoaded) + \
      'ipRangeExists: ' + str(ipRangeExists) + \
      'ipRangeError: ' + str(ipRangeError) + \
      'partyCreated: ' + str(partyCreated)
