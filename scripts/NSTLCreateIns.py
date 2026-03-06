#!/usr/bin/python
# input file format: party id, serial id

import django
import csv
import pandas as pd
import numpy
import sys,os
from netaddr import IPAddress, IPRange, IPNetwork
import xlsxwriter
from collections import defaultdict
import re
from django.db.models import Q

# format: serial id,cn name,en name,start ip,end ip
os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import IpRange, Party, PartyAffiliation
from party.serializers import PartySerializer
from common.common import isIpRangePrivate, validateIpRangeSize, validateIpRange, validateIpRangeOverlap

# Begin main program:

# Open the source file and load into memory.
IpRangeFilename = sys.argv[1]
# Processing Data

data = pd.read_excel(IpRangeFilename, index_col=None, usecols = "A,B,C",
        # encoding=encoding,
        na_filter=False,
        # dtype={'id': int, 'name_en': str, 'ip_update': str}
        )
output = []
errList = []

for index, row in data.iterrows():
    try:
        rowIndex = index + 2
        serialId = row['serial id']
        cn_name = row['cn name']
        en_name = row['en name']
        countryId = 127
        consortiumId = 31772

        # print serialId + ' ' + cn_name + ' ' + en_name

        if Party.objects.filter(name=en_name).exists():
            try:
                p = Party.objects.filter(name=en_name)[0]
                p.serialId = serialId
                p.save()
                print 'saved'
                continue
            except Exception as e:
                errList.append([serialId, cn_name, en_name, e.message])
                continue
        partySerializer = PartySerializer(
            data={'name': en_name, 'partyType': 'organization', 'country': countryId, 'serialId': serialId}, partial=True)
        if partySerializer.is_valid():
            partySerializer.save()
            print '[New Party Created] ' + en_name
        else:
            raise Exception('[Party serializer invalid] ' + \
                            'institution: ' + en_name)
        if consortiumId:
            partyId = partySerializer.data['partyId']
            childParty = Party.objects.get(partyId=partyId)
            parentParty = Party.objects.get(partyId=consortiumId)
            PartyAffiliation.objects.create(childPartyId=childParty, parentPartyId=parentParty)
            print '[PartyAffiliation Created] ' + \
                  'institution: ' + en_name + \
                  'consortium: ' + parentParty.name

        # partyId = models.AutoField(primary_key=True)
        # partyType = models.CharField(max_length=200, default='user')
        # name = models.CharField(max_length=200, default='')
        # display = models.BooleanField(default=True)
        # country = models.ForeignKey('Country', null=True, db_column="countryId")
        # consortiums = models.ManyToManyField('self', through="PartyAffiliation",
        #                                      through_fields=('childPartyId', 'parentPartyId'), symmetrical=False,
        #                                      related_name="PartyAffiliation")
        # label = models.CharField(max_length=64, null=True)
        # serialId = models.CharField(max_length=16, unique=True, null=True)
    except Exception as e:
        errList.append([serialId, cn_name, en_name, e.message])

if errList:
    errdf = pd.DataFrame(errList,
        columns=['serial id', 'cn name', 'en name', 'error'])

    errdf.to_excel('serial_id_party_id_loading_error.xlsx', engine='xlsxwriter', index=False)