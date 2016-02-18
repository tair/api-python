import django
import os
import csv

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import PartyAffiliation, Party

#Function to add one affiliation
def createAffiliation(institutionId, consortiumId):
    institution = Party.objects.get(partyId = institutionId)
    consortium = Party.objects.get(partyId = consortiumId)
    PartyAffiliation.objects.create(childPartyId=institution,parentPartyId=consortium)

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('partyAffiliationCSV.csv', 'rU') as f:
    reader = csv.reader(f,dialect=csv.excel_tab)
    partyAffiliatoinData = list(reader)

# Step2: Call function
for entry in partyAffiliatoinData:
    institutionId = entry[0].split(',')[0]
    consortiumId = entry[0].split(',')[1]
    createAffiliation(institutionId, consortiumId)
