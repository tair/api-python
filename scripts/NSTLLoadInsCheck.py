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

from party.models import IpRange, Party


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

input_dict= defaultdict(str)
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

    if serialId not in input_dict:
        input_dict[serialId] = en_name
    elif en_name != input_dict[serialId]:
        errList.append([serialId, cn_name, en_name, start, end, 'multiple ins name found'])
        errList.append([serialId, '', input_dict[serialId], '', '', 'multiple ins name found'])
        continue
    else:
        continue

    try:
        p = Party.objects.get(serialId=serialId)
        output.append([serialId, cn_name, en_name, start, end])
        output.append([p.serialId, '', p.name, '', '', p.partyId])
    except Exception as e:
        errList.append([serialId, cn_name, en_name, start, end, e.message])
        continue


df = pd.DataFrame(output,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip', 'partyId'])

errdf = pd.DataFrame(errList,
    columns=['serial id', 'cn name', 'en name', 'start ip','end ip','error'])

df.to_excel('NSTL_ins_check.xlsx', engine='xlsxwriter', index=False)
errdf.to_excel('NSTL_ins_check_error.xlsx', engine='xlsxwriter', index=False)

# errlog.close()