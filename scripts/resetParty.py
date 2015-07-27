#!/usr/bin/python  

import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from party.models import Party

Party.objects.all().delete()
