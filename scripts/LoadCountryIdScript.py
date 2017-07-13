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
orgCountriesFilename = raw_input('Please enter a file name(*.csv) for organization countires list:\n')

with open(orgCountriesFilename, 'rb') as f:
    reader = csv.reader(f)
    organizationCountryData = list(reader)

# Processing Data
print 'Processing Data'

for entry in organizationCountryData:
    organizationName = entry[0]
    countryName = entry[1]

    if Country.objects.all().filter(name=countryName).exists():
        countryId = Country.objects.get(name=countryName).countryId.countryId
    else:
        print 'cannot find country name: ' + countryName

    if Party.objects.all().filter(name=organizationName).exists():
        party = Party.objects.get(name=organizationName)
    else:
        print 'cannot find party: ' + organizationName

    data = {'countryId':countryId}

    serializer = PartySerializer(party, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
    else:
        print "cannot save party: " + organizationName
        print data

print 'Loading Complete'
