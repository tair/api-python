#!/usr/bin/python
# input file format: institution name, ip address, ip address change

import django
import sys
import os
import pandas as pd
from netaddr import IPAddress
import xlsxwriter

# format: serial id,cn name,en name,start ip,end ip
os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange
from common.common import (
    isIpRangePrivate,
    validateIpRangeSize,
    get_overlapping_ranges,
    exact_match_exists,
)

# Begin main program:

# Open the source file and load into memory.
IpRangeFilename = sys.argv[1]

data = pd.read_excel(IpRangeFilename, index_col=None, usecols="A,B,C,D,E",
        na_filter=False)
output = []
errList = []
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
    if count % 10 == 0:
        print(str(count) + '/' + str(len(data)))
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
        except Exception:
            errList.append([serialId, cn_name, en_name, start, end, 'ip range invalid'])
            continue

        # exact match: already in DB (one DB query)
        if exact_match_exists(start, end, IpRange):
            existing = get_overlapping_ranges(start, end, IpRange)
            for ipRange in existing:
                if ipRange.start == start and ipRange.end == end:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range exists'])
                    errList.append([ipRange.partyId.serialId if ipRange.partyId.serialId else '', '', ipRange.partyId.name, ipRange.start, ipRange.end, 'ip range exists', ipRange.ipRangeId])
                    toIgnore.add(str(ipRange.ipRangeId))
            continue

        # overlap check (one DB query per row)
        overlapping = get_overlapping_ranges(start, end, IpRange)
        overlap = False
        for ipRange in overlapping:
            range_serial = str(ipRange.partyId.serialId) if ipRange.partyId.serialId else ''
            range_names = ipRange.partyId.name
            range_ids_str = str(ipRange.ipRangeId)
            start_val = IPAddress(start)
            end_val = IPAddress(end)
            range_start = IPAddress(ipRange.start)
            range_end = IPAddress(ipRange.end)
            same_inst = str(serialId) == range_serial

            if start_val >= range_start and end_val <= range_end:
                overlap = True
                errList.append([serialId, cn_name, en_name, start, end, 'ip range contained'])
                errList.append([range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contained', range_ids_str])
                toIgnore.add(str(ipRange.ipRangeId))
            elif start_val <= range_start and end_val >= range_end:
                overlap = True
                if same_inst:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range contain existing in same institution'])
                    errList.append([range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contain existing in same institution', range_ids_str])
                else:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range contain existing in different institution'])
                    errList.append([range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range contain existing in different institution', range_ids_str])
                toExpire.add(str(ipRange.ipRangeId))
            else:
                overlap = True
                if same_inst:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range overlap in same institution'])
                    errList.append([range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range overlap in same institution', range_ids_str])
                else:
                    errList.append([serialId, cn_name, en_name, start, end, 'ip range overlap in different institution'])
                    errList.append([range_serial, '', range_names, ipRange.start, ipRange.end, 'ip range overlap in different institution', range_ids_str])
                toExpire.add(str(ipRange.ipRangeId))
        if not overlap:
            output.append([serialId, cn_name, en_name, start, end])
    except Exception as e:
        errList.append([serialId, cn_name, en_name, start, end, getattr(e, 'message', str(e))])
        continue

print('error IP ranges to ignore:' + ','.join(toIgnore))
print('total ' + str(len(toIgnore)))
print('IP ranges need to expire:' + ','.join(toExpire))
print('total ' + str(len(toExpire)))

df = pd.DataFrame(output,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip'])

errdf = pd.DataFrame(errList,
    columns=['serial id', 'cn name', 'en name', 'start ip', 'end ip', 'error', 'ip range id'])

df.to_excel('NSTL_all_ip_to_load.xlsx', engine='xlsxwriter', index=False)
errdf.to_excel('NSTL_all_ip_check_error.xlsx', engine='xlsxwriter', index=False)

# errlog.close()