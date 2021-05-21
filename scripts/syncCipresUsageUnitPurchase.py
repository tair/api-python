# execute by 
# echo "import scripts.syncCipresUsageUnitPurchase" | ./manage.py shell
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from subscription.models import UsageUnitPurchase
from authentication.models import Credential
from common.utils.cipresUtils import APICaller

purchases = UsageUnitPurchase.objects.filter(partnerId="cipres").filter(syncedToPartner=False)
caller = APICaller()

for purchase in purchases:
    userIdentifier = Credential.objects.filter(partyId=purchase.partyId).first().userIdentifier
    unitQty = purchase.quantity
    transactionId = purchase.transactionId
    purchaseDate = purchase.purchaseDate

    try:
        response = caller.postUnitPurchase(userIdentifier, unitQty, transactionId, purchaseDate)
        if response.status_code == 201:
            purchase.syncedToPartner = True
            purchase.save()
            message = "Synchornization succeed!"
        else:
            message = response.text
        status_code = response.status_code
    except Exception, e:
        status_code = "N/A"
        message = "Unexpected exception: %s" % (e)
        
    print """
    Try re-synchronizing CIPRES subscription to CIPRES database.
        Unit Purchase ID: %s
        Transaction ID: %s
        Purchase Time: %s
        User Identifier: %s
        Purchase Unit: %s
        HTTP status code: %s
        Message: %s
        """ % (purchase.purchaseId, transactionId, purchaseDate, userIdentifier, unitQty, status_code, message)