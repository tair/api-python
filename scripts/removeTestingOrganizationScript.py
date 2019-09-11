#!/usr/bin/python

import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from party.models import Party
from authentication.models import Credential

# Begin main program:

# Step1: Open the source CSV file and load into memory.
partyListFilename = input("Please enter a file name(*.csv) for party list(not organization_country):\n")

with open(partyListFilename, 'rb') as f:
    reader = csv.reader(f)
    partyListData = list(reader)

for entry in partyListData:

    if Party.objects.all().filter(name=entry[0]).exists():
        Party.objects.all().filter(name=entry[0]).delete()
        print('deleted: '+ entry[0])

