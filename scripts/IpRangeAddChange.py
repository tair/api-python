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
from common.common import ip2long, get_overlapping_ranges

# Begin main program:

# Open the source CSV file and load into memory.
IpRangeFilename = sys.argv[1]

with open(IpRangeFilename, 'rU') as f:
    reader = csv.reader(f)
    IpRangeListData = list(reader)

errlog = open("ipLoadingErrorLog.csv", "w+")
# Processing Data
print('Processing Data')

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
        # remove any blank spaces or non-ascii charactors from the ip ranges
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
            for i in range(len(startIpList)):
                while startIpList[i].startswith('0') and startIpList[i] != '0':
                    startIpList[i] = startIpList[i][1:]
            startIp = '.'.join(startIpList)

        if len(endIp.split('.')) == 4:
            endIpList = endIp.split('.')
            for i in range(len(endIpList)):
                while endIpList[i].startswith('0') and endIpList[i] != '0':
                    endIpList[i] = endIpList[i][1:]
            endIp = '.'.join(endIpList)

        try:
            if not Party.objects.filter(partyType='organization', name__iexact=institutionName).exists():
                overlapping = get_overlapping_ranges(startIp, endIp, IpRange)
                if overlapping:
                    potentialExistingParty[institutionName].update(r.partyId_id for r in overlapping)
                    continue
        except Exception as e:
            errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp)
            errlog.write(str(e) + '\n')
            raise Exception(str(e))

    except (ValidationError, AddrFormatError, IntegrityError, UnicodeDecodeError) as e:
        errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp + '\n')
        errlog.write(str(e) + '\n')
        continue

for k, v in potentialExistingParty.items():
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
            for i in range(len(startIpList)):
                while startIpList[i].startswith('0') and startIpList[i] != '0':
                    startIpList[i] = startIpList[i][1:]
            startIp = '.'.join(startIpList)

        if len(endIp.split('.')) == 4:
            endIpList = endIp.split('.')
            for i in range(len(endIpList)):
                while endIpList[i].startswith('0') and endIpList[i] != '0':
                    endIpList[i] = endIpList[i][1:]
            endIp = '.'.join(endIpList)


        if not Party.objects.filter(partyType='organization', name__iexact=institutionName).exists():
            if institutionName in potentialExistingParty:
                continue

        print('Processing: ' + institutionName)

        if actionType == 'create':
            partyId = None
            # when the party doesn't exist
            if not Party.objects.filter(partyType='organization', name__iexact=institutionName).exists():
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
                    print('[New Party Created] ' + institutionName)
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
                    print('[PartyAffiliation Created] ' +
                          'institution: ' + institutionName +
                          ' consortium: ' + parentParty.name)
                partyCreated += 1

            # when the party exists
            else:
                party_matches = Party.objects.filter(partyType='organization', name__iexact=institutionName)
                if party_matches.count() > 1:
                    raise Exception('[More than one party found with institution name] ' +
                                    ' type: ' + actionType +
                                    ' institution: ' + institutionName +
                                    ' start: ' + startIp +
                                    ' end: ' + endIp +
                                    ' parties: ' + ','.join([str(p.partyId) for p in party_matches]))
                partyId = party_matches.first().partyId
                if consortiumId:
                    childParty = Party.objects.get(partyId=partyId)
                    parentParty = Party.objects.get(partyId=consortiumId)
                    party, created = PartyAffiliation.objects.get_or_create(childPartyId=childParty, parentPartyId=parentParty)
                    if created:
                        print('[PartyAffiliation Created] ' +
                              'institution: ' + institutionName +
                              ' consortium: ' + parentParty.name)
                try:
                    start_long = ip2long(startIp)
                    end_long = ip2long(endIp)
                    if IpRange.objects.filter(partyId=partyId, startLong=start_long, endLong=end_long).exists():
                        print('[Ip range already exists] ' +
                              'type: ' + actionType +
                              ' institution: ' + institutionName +
                              ' start: ' + startIp +
                              ' end: ' + endIp)
                        ipRangeExists += 1
                        continue
                except Exception:
                    pass
            # create ip range
            ipRangeSerializer = IpRangeSerializer(data={'start': startIp, 'end': endIp, 'partyId': partyId}, partial=True)
            if ipRangeSerializer.is_valid():
                ipRangeSerializer.save()
                print('[IpRange Created] ' +
                      'type: ' + actionType +
                      ' institution: ' + institutionName +
                      ' start: ' + startIp +
                      ' end: ' + endIp)
                ipRangeLoaded += 1
            else:
                raise Exception('[Ip range serializer invalid] ' +
                                'type: ' + actionType +
                                ' institution: ' + institutionName +
                                ' start: ' + startIp +
                                ' end: ' + endIp)

        elif actionType == 'update':
            partyId = None
            # when the party doesn't exist
            if not queryset.filter(name__iexact=institutionName).exists():
                raise Exception('[Party does not exist] ' +
                                'type: ' + actionType +
                                ' institution: ' + institutionName +
                                ' start: ' + startIp +
                                ' end: ' + endIp)

            # when the party exists
            elif queryset.filter(name__iexact=institutionName).count() > 1:
                raise Exception('[More than one party found with institution name] ' +
                                'type: ' + actionType +
                                ' institution: ' + institutionName +
                                ' start: ' + startIp +
                                ' end: ' + endIp)
            else:
                partyId = queryset.filter(name__iexact=institutionName).first().partyId
                if partyId not in cleared:
                    IpRange.objects.all().filter(partyId=partyId).delete()
                    cleared.append(partyId)

            # create ip range
            ipRangeSerializer = IpRangeSerializer(data={'start': startIp, 'end': endIp, 'partyId': partyId}, partial=True)
            if ipRangeSerializer.is_valid():
                ipRangeSerializer.save()
                print('[IpRange Created] ' +
                      'type: ' + actionType +
                      ' institution: ' + institutionName +
                      ' start: ' + startIp +
                      ' end: ' + endIp)
                ipRangeLoaded += 1
            else:
                raise Exception('[Ip range serializer invalid] ' +
                                'type: ' + actionType +
                                ' institution: ' + institutionName +
                                ' start: ' + startIp +
                                ' end: ' + endIp)
    # except (ValidationError, AddrFormatError, IntegrityError, UnicodeDecodeError) as e:
    except Exception as e:
        ipRangeError += 1
        print('[IpRange Error] ' +
              'type: ' + actionType +
              ' institution: ' + institutionName +
              ' start: ' + startIp +
              ' end: ' + endIp)
        errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp + ' ')
        errlog.write(str(e) + '\n')
        continue
errlog.close()
print('Loading Complete: ' + '\n' +
      'ipRangeLoaded: ' + str(ipRangeLoaded) +
      ' ipRangeExists: ' + str(ipRangeExists) +
      ' ipRangeError: ' + str(ipRangeError) +
      ' partyCreated: ' + str(partyCreated))
