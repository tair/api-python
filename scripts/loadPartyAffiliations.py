import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import Affiliation, Party

#Function to add one affiliation
def createAffiliation(institutionId, consortiumId):
    institution = Party.objects.get(partyId = institutionId)
    consortium = Party.objects.get(partyId = consortiumId)
    Affiliation.objects.create(institutionId=institution,consortiumId=consortium)

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('Parites.csv', 'rb') as f:
    reader = csv.reader(f)
    partyAffiliatoinData = list(reader)

# Step2: Call function
for entry in partyAffiliatoinData:
    createAffiliation(entry[0], entry[1])

