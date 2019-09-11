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

# Open the source CSV file and load into memory.
orgCountriesFilename = input('Please enter a file name(*.csv) for organization countires list:\n')

with open(orgCountriesFilename, 'rb') as f:
    reader = csv.reader(f)
    organizationCountryData = list(reader)

# Processing Data
print('Processing Data')

for entry in organizationCountryData:
    organizationName = entry[0]
    countryName = entry[1]
    party = None
    countryId = None

    if Country.objects.all().filter(name=countryName).exists():
        countryId = Country.objects.get(name=countryName).countryId
    else:
        print('cannot find country name: ' + countryName)
        continue

    if Party.objects.all().filter(name=organizationName).exists():
        if Party.objects.all().filter(name=organizationName).count() > 1:
            print('more than one Party returned: ' + organizationName)
            continue
        party = Party.objects.get(name=organizationName)
    else:
        print('cannot find party: ' + organizationName)
        continue

    data = {'country':countryId}

    serializer = PartySerializer(party, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        print("cannot save party: " + organizationName)
        print(data)

print('Loading Complete')
