#!/usr/bin/python
import os

os.system('../manage.py migrate')
os.system('./setupDbScript.py')
os.system('./basicMigrationScript.py')
os.system('./countryMigration.py')
os.system('./userMigrationScript.py')
os.system('./subscriptionMigrationScript.py')
os.system('./personSubscriptionMigrationScript.py')
