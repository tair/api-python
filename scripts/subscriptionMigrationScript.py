#!/usr/bin/python

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import PartySerializer, IpRangeSerializer
from party.models import Country, Party
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('organization.csv', 'rb') as f:
    reader = csv.reader(f)
    organizationData = list(reader)


with open('subscribediprange.csv', 'rb') as f:
    reader = csv.reader(f)
    ipData = list(reader)

with open('organization_country.csv', 'rb') as f:
    reader = csv.reader(f)
    organizationCountryData = list(reader)

orgIdPartyId = {}

partnerId = 'tair'

monthLookup= {
    'JAN':'01',
    'FEB':'02',
    'MAR':'03',
    'APR':'04',
    'MAY':'05',
    'JUN':'06',
    'JUL':'07',
    'AUG':'08',
    'SEP':'09',
    'OCT':'10',
    'NOV':'11',
    'DEC':'12',
}

def parseYear(year):
    return str(2000+int(year))

def parseTime(inString):
    inArr = inString.split()
    date = inArr[0]
    dateArr = date.split('-')
    day = dateArr[0]
    month = monthLookup[dateArr[1]]
    year = parseYear(dateArr[2])

    timeArr = inArr[1].split('.')
    timeStr = "%s:%s:%s" % (timeArr[0], timeArr[1], timeArr[2])

    outString = "%s-%s-%sT%sZ" % (year, month, day, timeStr)
    return outString

# Initializing organization country
print("Initializing Organization Country Array")
organizationCountryArray = {}
for entry in organizationCountryData:
    organizationId = entry[0]
    if not organizationId.isdigit():
        continue
    organizationName = entry[1]
    countryName = entry[2]
    if countryName == 'China':
        countryName = "China, PR"
    if countryName == 'UK':
        countryName = 'United Kingdom'
    if entry[3] == 'Y':
        display = True
    else:
        display = False
    if Country.objects.all().filter(name=countryName).exists():
        countryId = int(Country.objects.all().get(name=countryName).countryId)
    else:
        countryId = None
    organizationCountryArray[organizationId] = [countryId, display]

print("Processing Data")
count = 0
for entry in organizationData:
    count += 1
    print(count)
    organizationId = entry[0]
    if not organizationId.isdigit():
        continue
    offset = 2
    organizationName = entry[1]
    if Party.objects.all().filter(name=organizationName).exists():
        print('organization already exists: '+'('+organizationId+')'+organizationName)
        continue
    while not entry[offset].isdigit():
        organizationName = "%s,%s" % (organizationName, entry[offset])
        offset += 1
    try:
        temp = organizationCountryArray[organizationId]
        countryId = temp[0]
        display = temp[1]
    except:
        countryId = None
        display = False
    organizationName = organizationName.decode('utf8')
    startDate = entry[offset+1]
    endDate = entry[offset+2]

    if not endDate or endDate == "":
        endDate = "01-JAN-99 01.00.00.000000000 AM AMERICA/LOS_ANGELES"
    startDate = parseTime(startDate)
    endDate = parseTime(endDate)

    data = {
        'name':organizationName,
        'partyType':'organization',
        'display':display,
        'country':countryId,
    }

    serializer = PartySerializer(data=data)
    if serializer.is_valid():
        serializer.save()

    partyId = serializer.data['partyId']
    orgIdPartyId[organizationId]=partyId
    data = {
        'partyId':partyId,
        'partnerId':partnerId,
        'startDate':startDate,
        'endDate':endDate,
    }
    serializer = SubscriptionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        print("CANNOT SAVE SUBSCRIPTION")
        print(data)

    subscriptionId = serializer.data['subscriptionId']
    data = {
        'subscriptionId':subscriptionId,
        'startDate':startDate,
        'endDate':endDate,
        'transactionDate':startDate,
        'transactionType':'create',
    }
    serializer = SubscriptionTransactionSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
print("DOING IP MIGRATION")

count = 0
for entry in ipData:
    count +=1
    print(count)
    organizationId = entry[0]
    if not organizationId.isdigit():
        continue
    start = entry[2]
    end = entry[3]
    if organizationId in orgIdPartyId:
        partyId = orgIdPartyId[organizationId]
    else:
        print('organization already exists: '+ organizationId)
        continue

    data = {
        'partyId':partyId,
        'start':start,
        'end':end,
    }
    serializer = IpRangeSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
    else:
        print("BAD IP")
        print(data)
