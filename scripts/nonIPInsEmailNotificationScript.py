#!/usr/bin/python

import django
import os
from django.core.mail import send_mail

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import Country, Party

parties = Party.objects.filter(iprange__isnull=True)
subject = "No Ip Ranges Institutions List"
message = "The following institutions have no ip ranges added:\n"

for party in parties:
    message += party.name + ' ' + party.partyId + '\n'

from_email = "subscriptions @ phoenixbioinformatics.org"
recipient_list = ["subscriptions@phoenixbioinformatics.org","qianli1987@arabidopsis.org"]
send_mail(subject=subject, message=message, from_email=from_email, recipient_list=recipient_list)
