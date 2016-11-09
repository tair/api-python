import django
import os
import csv
import hashlib

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import Party
from authentication.models import Credential

#Function to add one credential
def createCredential(partyId, username, password):
    party = Party.objects.get(partyId = partyId)
    password = hashlib.sha1(password).hexdigest()
    Credential.objects.create(partyId=party,username=username, password=password)

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('loadCredentialInfile20161108.csv', 'rU') as f:
    reader = csv.reader(f,dialect=csv.excel_tab)
    credentialData = list(reader)

# Step2: Call function
for entry in credentialData:
    list = entry[0].split(',')
    partyId = list[0]
    username = list[1]
    password = list[2]
    createCredential(partyId, username, password)
