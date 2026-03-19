# execute by 
# echo "import scripts.syncCyVerseAddonOptions" | ./manage.py shell
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from django.utils import timezone
from subscription.models import UsageAddonOption
from authentication.models import Credential
from common.utils.cyverseUtils import CyVerseClient

client = CyVerseClient()
localAddonOptions = UsageAddonOption.objects

try:
    cyverseAddonOptions = client.getAddonOptions()
    for option in cyverseAddonOptions:
        description = option['description']
        name = option['name']
        uuid = option['uuid']
        print """
            Getting CyVerse add on options.
                name: %s
                description: %s
                uuid: %s
                """ % (name, description, uuid) 
except RuntimeError as error: 
        print """
            Getting CyVerse add on options failed.
                Error Message: %s
                """ % (error) 