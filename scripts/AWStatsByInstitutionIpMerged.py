#!/usr/bin/python
# will generate report by institution together with their ips
# file format:
# columns for IP, page visits, page hits

import django
import os
import csv
import sys
import pandas as pd
from collections import defaultdict
from netaddr import IPAddress
import datetime
from io import open

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange, Party

# Begin main program:

# Open the source CSV file and load into memory.
IpRangeFilename = sys.argv[1]

with open(IpRangeFilename, 'rb') as f:
    reader = csv.reader(f)
    dataList = list(reader)

# Processing Data
print 'Processing AWStats Data'

ipranges = IpRange.objects.all()

partyDict = defaultdict(lambda: list([0,0,[]]))

lineNum = 1
for entry in dataList:
    ip = entry[0]
    pages = int(entry[1])
    hits = int(entry[2])
    found = False
    try:
        IPAddress(ip)
    except:
        partyDict[u'invalid_ip_'+ip][0] += pages
        partyDict[u'invalid_ip_'+ip][1] += hits
        print str(lineNum) + ' processed'
        lineNum += 1
        continue
    for iprange in ipranges:
        if IPAddress(iprange.start)<= IPAddress(ip) <= IPAddress(iprange.end):
            partyId = iprange.partyId.partyId
            name = Party.objects.get(partyId=partyId).name
            partyDict[name][0] += pages
            partyDict[name][1] += hits
            partyDict[name][2].append([ip, pages, hits])
            found = True
            break
    if not found:
        partyDict[u'unknown'][0] += pages
        partyDict[u'unknown'][1] += hits
    print str(lineNum) + ' processed'
    lineNum += 1

instOut = []
detailOut = []
for k,v in partyDict.iteritems():
    detailOut.append([k, v[0], v[1]])
    instOut.append([k, v[0], v[1]])
    for ipData in v[2]:
        detailOut.append(ipData)

dfInst = pd.DataFrame(instOut, columns=['institution', 'page views', 'page hits'])
dfDetail = pd.DataFrame(detailOut, columns=['', 'page views', 'page hits'])

# Create a Pandas Excel writer using XlsxWriter as the engine.
with pd.ExcelWriter('institutionIpPageViews'+str(datetime.datetime.now().strftime('%Y%m%d_%H%M%S'))+'.xlsx', engine='xlsxwriter') as writer:
    # Convert the dataframe to an XlsxWriter Excel object.
    dfInst.to_excel(writer, sheet_name='institution', index=False, encoding='utf-8')
    dfDetail.to_excel(writer, sheet_name='detail', index=False, encoding='utf-8')