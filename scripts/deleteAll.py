#!/usr/bin/python  

import csv
import hashlib
import MySQLdb

import django
import requests
import json

import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from partner.models import Partner
from authorization.models import AccessType
from authorization.models import UriPattern
from apikey.models import ApiKey

Partner.objects.all().delete()
AccessType.objects.all().delete()
UriPattern.objects.all().delete()
ApiKey.objects.all().delete()
