#!/usr/bin/python

import django
import os
import io
import xlsxwriter
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import IpRangeSerializer, PartySerializer
from party.models import IpRange, Party, PartyAffiliation
from loggingapp.models import PageView

consortiumId = int(raw_input('Please enter consortium Id:\n'))

consortium = Party.objects.get(partyId=consortiumId)
partyList = Party.objects.get(partyId=consortiumId).Affiliation.all()

ipRangeList = []
for party in partyList:
    ipRangeList.extend(IpRange.objects.all().filter(partyId=party))

pageViewList = []
for ipRange in ipRangeList:
    pageViewList.extend(PageView.objects.all().filter(ip__gte = ipRange.start, ip__lte = ipRange.end))

output = io.BytesIO()
workbook = xlsxwriter.Workbook(output, {'in_memory': True})
worksheet = workbook.add_worksheet()

# Write PageView rows
for pageView in pageViewList:
    worksheet.write(pageView.pageViewId, pageView.uri, pageView.partyId, pageView.pageViewDate, pageView.sessionId, pageView.ip)

# Close the workbook before streaming the data.
workbook.close()

# Rewind the buffer.
output.seek(0)
