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

IPV4_DOTTED_QUAD_RE = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")


def normalize_csv_ip_range_fields(start_ip, end_ip, institution_name, errlog):
    """
    Strip, handle '-' compact form, empty start/end fallback, IPv4 dotted-quad check,
    leading-zero removal. Returns (start_ip, end_ip) or (None, None) if row should be skipped.
    """
    start_ip = start_ip.replace(" ", "").strip()
    end_ip = end_ip.replace(" ", "").strip()

    if '-' in start_ip:
        if end_ip:
            errlog.write("Error institution: " + institution_name + " invalid ip: " + start_ip + " " + end_ip + '\n')
            return None, None
        if len(start_ip.split('-')) != 2:
            errlog.write("Error institution: " + institution_name + " invalid starting ip: " + start_ip + '\n')
            return None, None
        s, e = start_ip.split('-')
        start_ip = s
        l = s.split('.')[:3]
        l.append(e)
        end_ip = '.'.join(l)

    if not start_ip:
        start_ip = end_ip
    if not end_ip:
        end_ip = start_ip

    if not IPV4_DOTTED_QUAD_RE.match(start_ip):
        errlog.write("Error institution: " + institution_name + " not ipv4 format: " + start_ip + '\n')
        return None, None
    if not IPV4_DOTTED_QUAD_RE.match(end_ip):
        errlog.write("Error institution: " + institution_name + " not ipv4 format: " + end_ip + '\n')
        return None, None

    if len(start_ip.split('.')) == 4:
        start_ip_list = start_ip.split('.')
        for i in range(len(start_ip_list)):
            while start_ip_list[i].startswith('0') and start_ip_list[i] != '0':
                start_ip_list[i] = start_ip_list[i][1:]
        start_ip = '.'.join(start_ip_list)

    if len(end_ip.split('.')) == 4:
        end_ip_list = end_ip.split('.')
        for i in range(len(end_ip_list)):
            while end_ip_list[i].startswith('0') and end_ip_list[i] != '0':
                end_ip_list[i] = end_ip_list[i][1:]
        end_ip = '.'.join(end_ip_list)

    return start_ip, end_ip


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
        startIp, endIp = normalize_csv_ip_range_fields(startIp, endIp, institutionName, errlog)
        if startIp is None:
            continue

        try:
            if not Party.objects.filter(partyType='organization', name__iexact=institutionName).exists():
                overlapping = get_overlapping_ranges(startIp, endIp, IpRange)
                if overlapping:
                    potentialExistingParty[institutionName].update(r.partyId_id for r in overlapping)
                    continue
        except Exception as e:
            errlog.write('Error institution: ' + institutionName + ' ' + startIp + " " + endIp)
            errlog.write(str(e) + '\n')
            continue

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

        startIp, endIp = normalize_csv_ip_range_fields(startIp, endIp, institutionName, errlog)
        if startIp is None:
            continue

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
