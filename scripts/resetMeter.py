#!/usr/bin/python  

import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from metering.models import IpAddressCount

IpAddressCount.objects.all().delete()
