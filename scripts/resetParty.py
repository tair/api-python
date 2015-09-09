#!/usr/bin/python  

import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from party.models import Party
from authentication.models import Credential

Party.objects.all().delete()
