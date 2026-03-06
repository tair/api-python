#!/usr/bin/python
# this file is used for the case of non-NSTL bulk load and might have issues.
# input file format: institution name, ip address, ip address change

import django
import os
import csv
import sys
import re
from netaddr import IPNetwork, IPAddress

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange

# Begin main program:

# Open the source CSV file and load into memory.
IpRangeFilename = sys.argv[1]

with open(IpRangeFilename, 'rb') as f:
    reader = csv.reader(f)
    IpRangeListData = list(reader)

errlog = open("ipCheckError.csv", "w+")
iptoadd = open("ipToAdd.csv", "w+")
# Processing Data
print 'Processing Data'

for entry in IpRangeListData:
    try:
        institutionName = entry[0]
        ips1 = entry[1]
        ips2 = entry[2]
        print institutionName
        print ips1
        print ips2
        cols = [ips1, ips2]
        for i in range(len(cols)):
            if cols[i]:
                ipList = cols[i].split(';')
                for iprange in ipList:
                    try:
                        if len(iprange.split('.')) == 4 and len(iprange.split('-')) == 3 and \
                                '-' in iprange.split('.')[2] and '-' in iprange.split('.')[3]:
                            start = '.'.join(iprange.split('.')[:2] + [iprange.split('.')[2].split('-')[0], iprange.split('.')[3].split('-')[0]])
                            end = '.'.join(iprange.split('.')[:2] + [iprange.split('.')[2].split('-')[1], iprange.split('.')[3].split('-')[1]])
                        elif len(iprange.split('-')) == 2:
                            start, end = iprange.split('-')
                            if len(start.split('.')) == 4 and len(end.split('.')) == 1:
                                end = '.'.join(start.split('.')[:3] + [end])
                                print end
                            elif len(start.split('.')) == 3 and len(end.split('.')) == 2 and end.split('.')[1] == '*':
                                end = '.'.join(start.split('.')[:2] + end.split('.')[:1] + ['255'])
                                start += '.0'
                            elif len(start.split('.')) == 4 and len(end.split('.')) == 2 and end.split('.')[0] != '*' and end.split('.')[1] != '*':
                                end = '.'.join(start.split('.')[:2] + end.split('.'))
                            elif len(start.split('.')) == 4 and len(end.split('.')) == 4:
                                if start.split('.')[3] == '*' and end.split('.')[3] == '*':
                                    start = '.'.join(start.split('.')[:3] + ['0'])
                                    end = '.'.join(end.split('.')[:3] + ['255'])
                                else:
                                    startList = [block.lstrip('0') or '0' for block in start.split('.')]
                                    endList = [block.lstrip('0') or '0' for block in end.split('.')]
                                    start = '.'.join(startList)
                                    end = '.'.join(endList)
                        elif len(iprange.split('-')) == 1:
                            if len(iprange.split('.')) == 4 and iprange.split('.')[2] == '*' and iprange.split('.')[3] == '*':
                                start = '.'.join(iprange.split('.')[:2] + ['0','0'])
                                end = '.'.join(iprange.split('.')[:2] + ['255','255'])
                                print start, end
                            elif len(iprange.split('.')) == 4 and iprange.split('.')[3] == '*':
                                start = '.'.join(iprange.split('.')[:3] + ['0'])
                                end = '.'.join(iprange.split('.')[:3] + ['255'])
                                print start, end
                            elif '/' in iprange.split('.')[3]:
                                ipNetwork = IPNetwork(iprange)
                                start = str(IPAddress(ipNetwork.first))
                                end = str(IPAddress(ipNetwork.last))
                            else:
                                start = end = iprange.split('-')[0]
                        elif len(iprange.split('-')) > 2:
                            errlog.write(','.join(['ips' + str(i+1), institutionName, iprange, 'too many ips', '\n']))
                            continue
                        else:
                            errlog.write(','.join(['ips' + str(i+1), institutionName, iprange, 'no ips', '\n']))
                            continue
                        start.replace(" ", "")
                        end.replace(" ", "")
                        if not re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").match(start):
                            errlog.write(','.join(['ips' + str(i+1), institutionName, 'start', start, '\n']))
                        elif not IpRange.objects.all().filter(start=start).exists():
                            iptoadd.write(','.join(['ips' + str(i+1), institutionName, 'start', start, '\n']))
                        if not re.compile("^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$").match(end):
                            errlog.write(','.join(['ips' + str(i+1), institutionName, 'end', end, '\n']))
                        elif not IpRange.objects.all().filter(end=end).exists():
                            iptoadd.write(','.join(['ips' + str(i+1), institutionName, 'end', end, '\n']))
                    except Exception as e:
                        errlog.write(','.join(['ips' + str(i+1) + ' other', institutionName, iprange, str(e), '\n']))
                        continue

    except Exception as e:
        errlog.write(','.join(['other',institutionName, 'ips1',ips1, 'ips2',ips2, str(e),'\n']))
        continue