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

for entry in Party.objects.all():
    print entry[0] + ", " + entry[1] + ', ' + entry[2]  + entry[3] + entry[4] + entry[5] +'\n'

for entry in Country.objects.all():
    print entry[0] + ", " + entry[1] + '\n'
