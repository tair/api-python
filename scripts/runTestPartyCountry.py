#!/usr/bin/python

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import Country, Party

# Begin main program:

instance = Party(partyType = 'organization', name = 'testPartybyQian', display=True)
instance.save()

# Step1: Open the source CSV file and load into memory.
with open('organization.csv', 'rb') as f:
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
        countryName = "People's Republic of China"
    if countryName == 'UK':
        countryName = 'United Kingdom'
    if entry[3] == 'Y':
        display = True
    else:
        display = False
    if Party.objects.all().filter(name=organizationName).exists():
        countryId = int(Party.objects.all().filter(name=organizationName)[0].country.countryId)
        print(organizationName + ", " + str(countryId) + "\n")
        # if Party.objects.all().filter(name=organizationName)[1].exists():
        #     countryId = int(Party.objects.all().filter(name=organizationName)[1].country.countryId)
        #     print organizationName + ", " + str(countryId) + "\n"
        #     if Party.objects.all().filter(name=organizationName)[2].exists():
        #         countryId = int(Party.objects.all().filter(name=organizationName)[2].country.countryId)
        #         print organizationName + ", " + str(countryId) + "\n"

    else:
        countryId = None;
    #print organizationName + ", " + countryId + "\n"
    #organizationCountryArray[organizationId] = [countryId, display]
