#!/usr/bin/python

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import PartySerializer
from subscription.serializers import SubscriptionSerializer, SubscriptionTransactionSerializer
from authentication.models import Credential

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
    dateArr = inString.split('-')
    day = dateArr[0]
    month = monthLookup[dateArr[1]]
    year = parseYear(dateArr[2])
    outString = "%s-%s-%sT%sZ" % (year, month, day, "00:00:00")
    return outString

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('personSubscription.csv', 'rb') as f:
    reader = csv.reader(f)
    personData = list(reader)


count = 0
partnerId = "tair"
for entry in personData:
    count += 1
    print(count)
    communityId = entry[0]
    if not communityId.isdigit():
        continue
    expirationDate = entry[1]

    cred = Credential.objects.all().filter(userIdentifier=communityId)
    if len(cred) > 0:
        partyId = cred[0].partyId.partyId
    else:
        print("not good %s" % communityId)
        continue

    startDate = parseTime("21-DEC-12")
    endDate = parseTime(expirationDate)
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
