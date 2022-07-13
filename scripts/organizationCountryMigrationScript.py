#!/usr/bin/python

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.serializers import PartySerializer
from party.models import Country, Party

# Begin main program:

# Step1: Open the source CSV file and load into memory.
organizationFilename = input("Please enter a file name(*.csv) for organization list(not organization_country):\n")

with open(organizationFilename, 'rb') as f:
    reader = csv.reader(f)
    organizationData = list(reader)

with open('organization_country.csv', 'rb') as f:
    reader = csv.reader(f)
    organizationCountryData = list(reader)

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
        countryId = None;
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

    data = {
        'name':organizationName,
        'partyType':'organization',
        'display':display,
        'country':countryId,
    }

    if Party.objects.all().filter(name=organizationName).exists():
        for partyInstance in Party.objects.all().filter(name=organizationName):

            serializer = PartySerializer(partyInstance, data=data)
            if serializer.is_valid():
                serializer.save()
            else:
                print("CANNOT SAVE PARTY")
                print(data)
    else:
        print("organizationName NOT FOUND: "+organizationName)
