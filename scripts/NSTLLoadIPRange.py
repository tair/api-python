#!/usr/bin/python
# input file format: serial id, cn name, en name, start ip, end ip

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

from party.models import Party, IpRange, PartyAffiliation, Country
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
    for ipr in ranges[1:]:
        if IPAddress(ipr[0]) <= IPAddress(res[-1][1]):
            res[-1][1] = str(max(IPAddress(ipr[1]), IPAddress(res[-1][1])))
            res[-1][2].update(ipr[2])
            res[-1][3].update(ipr[3])
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
ipRangeList = IpRange.objects.all()

# # build merge ranges:
# print('building merged list......')
# toMergeList = []
# cnt = 0
# print(len(ipRangeList))
# for ipRange in ipRangeList:
#     if cnt%10 == 0:
#         print cnt
#     cnt += 1
#     toMergeList.append([ipRange.start, ipRange.end, set([ipRange.partyId.name]), set([ipRange.partyId.serialId])])
# mergedList = mergeRanges(toMergeList)

count = 0
print(len(data))
for index, row in data.iterrows():
    rowIndex = index + 2
    serialId = row['serial id']
    cn_name = row['cn name']
    en_name = row['en name']
    start = row['start ip']
    end = row['end ip']
    # print(','.join([str(serialId),cn_name,en_name,start,end]))
    if count % 10 == 0:
        print (str(count) + '/' + str(len(data)))
    count += 1
    output.append([serialId,cn_name,en_name,start,end])
#
#     try:
#         # check size limit
#         if not validateIpRangeSize(start, end):
#             errList.append([serialId, cn_name, en_name, start, end, 'ip range too large'])
#             continue
#
#         # check private
#         if isIpRangePrivate(start, end):
#             errList.append([serialId, cn_name, en_name, start, end, 'ip range private'])
#             continue
#         # check 255
#         if start.startswith('255') or end.startswith('255'):
#             errList.append([serialId, cn_name, en_name, start, end, 'ip range invalid'])
#             continue
#
#         # existing
#         exists = False
#         for ipRange in ipRangeList:
#             if IPAddress(start) == IPAddress(ipRange.start) and IPAddress(end) == IPAddress(ipRange.end):
#                 exists = True
#                 errList.append([serialId, cn_name, en_name, start, end, 'ip range exists'])
#                 errList.append(['', '', ipRange.partyId.name, ipRange.start, ipRange.end, 'ip range exists'])
#         if exists:
#             continue
#
#         overlap = False
#         # check overlap
#         for ipRange in mergedList:
#             # no overlap
#             if IPAddress(start) > IPAddress(ipRange[1]) or IPAddress(end) < IPAddress(ipRange[0]):
#                 continue
#             # ip to load contained in existing
#             elif IPAddress(start) >= IPAddress(ipRange[0]) and IPAddress(end) <= IPAddress(ipRange[1]):
#                 overlap = True
#                 errList.append([serialId, cn_name, en_name, start, end, 'ip range contained'])
#                 errList.append(['', '', ';'.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range contained'])
#             # ip to load contains existing
#             elif IPAddress(start) <= IPAddress(ipRange[0]) and IPAddress(end) >= IPAddress(ipRange[1]):
#                 if str(serialId) in ipRange[3]:
#                     continue
#                 print(ipRange[3],serialId)
#                 print(type(ipRange[3]))
#                 print(type(serialId))
#                 overlap = True
#                 errList.append([serialId, cn_name, en_name, start, end, 'ip range contain existing'])
#                 errList.append([';'.join(ipRange[3]), '', ';'.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range contain existing'])
#             # partial overlap
#             else:
#                 if str(serialId) in ipRange[3]:
#                     continue
#                 print(ipRange[3], serialId)
#                 print(type(ipRange[3]))
#                 print(type(serialId))
#                 overlap = True
#                 errList.append([serialId, cn_name, en_name, start, end, 'ip range overlap'])
#                 errList.append([';'.join(ipRange[3]), '', ';'.join(ipRange[2]), ipRange[0], ipRange[1], 'ip range overlap'])
#         if not overlap:
#             output.append([serialId,cn_name,en_name,start,end])
#     except Exception as e:
#         errList.append([serialId,cn_name,en_name,start,end,e.message])
#         continue
#
# if errList:
#
#     errdf = pd.DataFrame(errList,
#     columns=['serial id', 'cn name', 'en name', 'start ip','end ip'])
#
#     errdf.to_excel('NSTL_all_ip_load_check_error.xlsx', engine='xlsxwriter', index=False)
#     sys.exit()

# diffList = []
# for serialId,cn_name,en_name,start,end in output:
#
#     p=Party.objects.get(serialId=serialId)
#     # ipr = IpRange(start=start, end=end, partyId=p)
#     if en_name.lower().replace(' ', '').replace('\'','') != p.name.lower().replace(' ', '').replace('\'',''):
#         diffList.append([p.name, serialId,cn_name,en_name,start,end])
#
# if diffList:
#     diffdf = pd.DataFrame(diffList,
#     columns=['db name', 'serial id', 'cn name', 'en name', 'start ip','end ip'])
#     diffdf.to_excel('NSTL_all_ip_load_name_error.xlsx', engine='xlsxwriter', index=False)
#     sys.exit()
loadingErr=[]
for serialId,cn_name,en_name,start,end in output:
    print(serialId)
    try:
        p = None
        if not Party.objects.filter(serialId=serialId).exists():
            country= Country.objects.get(countryId = 127)
            p = Party.objects.create(partyType='organization', serialId=serialId,display = True, name = en_name, country=country)
            NSTL = Party.objects.get(partyId= 31772)
            PartyAffiliation.objects.create(childPartyId=p, parentPartyId=NSTL)
        else:
            p = Party.objects.get(serialId=serialId)
        IpRange.objects.create(partyId=p, start=start, end=end)
    except Exception as e:
        loadingErr.append([serialId, cn_name, en_name, start, end, e.message])
        continue

if loadingErr:
    print('error saved in NSTL_all_ip_load_runtime_error.xlsx')
    diffdf = pd.DataFrame(loadingErr,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip', 'error'])
    diffdf.to_excel('NSTL_all_ip_load_runtime_error.xlsx', engine='xlsxwriter', index=False)