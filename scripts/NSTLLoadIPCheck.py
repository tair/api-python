#!/usr/bin/python
# input file format: institution name, ip address, ip address change

import django
import csv
import pandas as pd
import numpy
import sys,os
from netaddr import IPAddress, IPRange, IPNetwork
import xlsxwriter
from collections import defaultdict
import re

# format: serial id,cn name,en name,start ip,end ip
os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange
from common.common import isIpRangePrivate, validateIpRangeSize, validateIpRange, validateIpRangeOverlap

# helper function:
def mergeRanges(ranges):
    """
    :type intervals: List[Interval]
    :rtype: List[Interval]
    """
    if ranges == []:
        return []
    ranges.sort(key=lambda x: IPAddress(x[0]))
    res = [ranges[0]]
    # ranges: [start:str, end:str, partyIds:set, serialIds:set, ipRangeIds:set]
    for ipr in ranges[1:]:
        if IPAddress(ipr[0]) <= IPAddress(res[-1][1]):
            res[-1][1] = str(max(IPAddress(ipr[1]), IPAddress(res[-1][1])))
            res[-1][2].update(ipr[2])
            res[-1][3].update(ipr[3])
            res[-1][4].update(ipr[4])
        else:
            res.append(ipr)
    return res


# Begin main program:

# Open the source file and load into memory.
IpRangeFilename = sys.argv[1]


# errlog = open("NSTL_after_2015_check_error.csv", "w+")
# Processing Data

data = pd.read_excel(IpRangeFilename, index_col=None, usecols = "A,B,C,D,E",
        # encoding=encoding,
        na_filter=False,
        # dtype={'id': int, 'name_en': str, 'ip_update': str}
        )
output = []
errList = []
ipRangeList = IpRange.objects.all().filter(expiredAt=None)

# build merge ranges:
print('building merged list......')
toMergeList = []
cnt = 0
print(len(ipRangeList))
for ipRange in ipRangeList:
    if cnt%10 == 0:
        print cnt
    cnt += 1
    # toMergeList: [start:str, end:str, partyIds:set, serialIds:set, ipRangeIds:set]
    toMergeList.append([ipRange.start, ipRange.end, set([ipRange.partyId.name]), set([ipRange.partyId.serialId]), set([str(ipRange.ipRangeId)])])
mergedList = mergeRanges(toMergeList)

toExpire = set()
toIgnore = set()
count = 0
print(len(data))
for index, row in data.iterrows():
    rowIndex = index + 2
    serialId = row['serial id']
    cn_name = row['cn name']
    en_name = row['en name']
    start = row['start ip']
    end = row['end ip']
    if start and not end:
        end = start
    # print(','.join([str(serialId),cn_name,en_name,start,end]))
    if count % 10 == 0:
        print (str(count) + '/' + str(len(data)))
    count += 1

    try:
        # check size limit
        if not validateIpRangeSize(start, end):
            errList.append([serialId, cn_name, en_name, start, end, 'ip range too large'])
            continue

        # check private
        if isIpRangePrivate(start, end):
            errList.append([serialId, cn_name, en_name, start, end, 'ip range private'])
            continue
        # check 255
        if start.startswith('255') or end.startswith('255'):
            errList.append([serialId, cn_name, en_name, start, end, 'ip range invalid'])
            continue

        try:
            IPAddress(start)
            IPAddress(end)
        except:
            errList.append([serialId, cn_name, en_name, start, end, 'ip range invalid'])
            continue

        # existing
        exists = False
        for ipRange in ipRangeList:
            if IPAddress(start) == IPAddress(ipRange.start) and IPAddress(end) == IPAddress(ipRange.end):
                exists = True
                errList.append([serialId, cn_name, en_name, start, end, 'ip range exists'])
                errList.append([ipRange.partyId.serialId if ipRange.partyId.serialId else '', '', ipRange.partyId.name, ipRange.start, ipRange.end, 'ip range exists', ipRange.ipRangeId])
                toIgnore.update(set([str(ipRange.ipRangeId)]))
        if exists:
            continue

        overlap = False
        # check overlap
        for ipRange in mergedList: # ipRange: [start:str, end:str, partyIds:set, serialIds:set, ipRangeIds:set]
            # no overlap
            if IPAddress(start) > IPAddress(ipRange[1]) or IPAddress(end) < IPAddress(ipRange[0]):
                continue
            # ip to load contained in existing
            elif IPAddress(start) >= IPAddress(ipRange[0]) and IPAddress(end) <= IPAddress(ipRange[1]):
                overlap = True
                errList.append([serialId, cn_name, en_name, start, end, 'ip range contained'])
                errList.append([ipRange[3] if ipRange[3] else '', '', ','.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range contained', ','.join(ipRange[4])])
                toIgnore.update(ipRange[4])
            # ip to load contains existing
            elif IPAddress(start) <= IPAddress(ipRange[0]) and IPAddress(end) >= IPAddress(ipRange[1]):
                print(ipRange[3],serialId)
                print(type(ipRange[3]))
                print(type(serialId))
                overlap = True
                if str(serialId) in ipRange[3]:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range contain existing in same institution'])
                    errList.append([ipRange[3] if ipRange[3] else '', '', ','.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range contain existing in same institution', ','.join(ipRange[4])])
                else:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range contain existing in different institution'])
                    errList.append([ipRange[3] if ipRange[3] else '', '', ','.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range contain existing in different institution', ','.join(ipRange[4])])
                toExpire.update(ipRange[4])
            # partial overlap
            else:
                print(ipRange[3], serialId)
                print(type(ipRange[3]))
                print(type(serialId))
                overlap = True
                if str(serialId) in ipRange[3]:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range overlap in same institution'])
                    errList.append([ipRange[3] if ipRange[3] else '', '', ','.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range overlap in same institution', ','.join(ipRange[4])])
                else:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range overlap in different institution'])
                    errList.append([ipRange[3] if ipRange[3] else '', '', ','.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range overlap in different institution', ','.join(ipRange[4])])
                toExpire.update(ipRange[4])
        if not overlap:
            output.append([serialId,cn_name,en_name,start,end])
    except Exception as e:
        errList.append([serialId,cn_name,en_name,start,end,e.message])
        continue

# errList.append(','.join(toExpire))
print 'error IP ranges to ignore:' + ','.join(toIgnore)
print 'total' + str(len(toIgnore))
print 'IP ranges need to expire:' + ','.join(toExpire)
print 'total' + str(len(toExpire))

df = pd.DataFrame(output,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip'])

errdf = pd.DataFrame(errList,
    columns=['serial id', 'cn name', 'en name', 'start ip', 'end ip', 'error', 'ip range id'])

df.to_excel('NSTL_all_ip_to_load.xlsx', engine='xlsxwriter', index=False)
errdf.to_excel('NSTL_all_ip_check_error.xlsx', engine='xlsxwriter', index=False)

# errlog.close()