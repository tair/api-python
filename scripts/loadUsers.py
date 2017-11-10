import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from django.contrib.auth.models import User
from authentication.models import Credential

for row in Credential.objects.all():
    try:
        row.user = User.objects.get(username=row.username+'_'+row.partnerId.partnerId)
        row.user.set_password('phoenix_test')
        row.user.save()
        try:
            row.save()
        except Exception:
            print 'Loading User Error: username: ' + row.username + 'Party ID: ' + str(row.partyId.partyId)
        print row.username+'_'+row.partnerId.partnerId + ' retrieved and loaded'
    except:
        try:
            tempUser = User.objects.create_user(username=row.username+'_'+row.partnerId.partnerId, password='phoenix_test')
            tempUser.save()
        except Exception:
            print 'Loading User Error: username: ' + row.username + 'Party ID: ' + str(row.partyId.partyId)
        row.user = tempUser
        try:
            row.save()
        except Exception:
            print 'Loading User Error: username: ' + row.username + 'Party ID: ' + str(row.partyId.partyId)
        print row.username+'_'+row.partnerId.partnerId + ' created and loaded'
    # row.save()

print '==========   User loading finished   =========='
