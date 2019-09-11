import django
import os
import csv
import hashlib
import json

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from authentication.serializers import CredentialSerializer

# Begin main program:

# Step1: Open the source CSV file and load into memory.
with open('testAccounts0329.csv', 'rU') as f:
    reader = csv.reader(f,dialect=csv.excel_tab)
    createAccountsData = list(reader)

# Step2: create acconts
data = {}
for entry in createAccountsData:
    data['email'] = entry[0].split(',')[0]
    data['institution'] = entry[0].split(',')[1]
    data['partyId'] = entry[0].split(',')[2]
    data['username'] = entry[0].split(',')[3]
    password = entry[0].split(',')[4]
    data['password'] = hashlib.sha1(password).hexdigest()
    data['partnerId'] = 'phoenix'
    serializer = CredentialSerializer(data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        print("user record loaded: ")
        print(json.dumps(serializer.data))
    else:
        print("user record not added: ")
        print(serializer.errors)

