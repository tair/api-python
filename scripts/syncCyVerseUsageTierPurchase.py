# execute by 
# echo "import scripts.syncCyVerseUsageTierPurchase" | ./manage.py shell
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from django.utils import timezone
from subscription.models import UsageTierPurchase
from subscription.controls import PaymentControl
from authentication.models import Credential
from common.utils.cyverseUtils import CyVerseClient

client = CyVerseClient()
unsyncedPurchases = UsageTierPurchase.objects.filter(partnerId="cyverse").filter(syncedToPartner=False)

for purchase in unsyncedPurchases:
    username = Credential.objects.filter(partyId=purchase.partyId).first().username
    termName = purchase.tierId.name
    termDuration = purchase.tierId.durationInDays

    try:
        client.postTierPurchase(username, termName)
        subscription = client.getSubscriptionTier(username)
        if (subscription['tier'] != termName):
            raise RuntimeError("CyVerse tier name %s and local tier name %s does not match" % (subscription['tier'], termName))
        purchase.partnerUUID = subscription['uuid']
        purchaseDate = timezone.now()
        endDate = PaymentControl.getExpirationDate(purchaseDate, termDuration)
        purchase.purchaseDate = purchaseDate
        purchase.endDate = endDate
        purchase.syncedToPartner = True
        purchase.save()
        print """
            Synchronizing CyVerse subscription to CyVerse database succeeded.
                Tier Purchase ID: %s
                Purchase Time: %s
                User Name: %s
                Term: %s
                Partner UUID: %s
                """ % (purchase.purchaseId, purchaseDate, username, termName, subscription['uuid'])
    except RuntimeError as error:
        print """
            Synchronizing CyVerse subscription to CyVerse database failed.
                Tier Purchase ID: %s
                User Name: %s
                Term: %s
                Error Message: %s
                """ % (purchase.purchaseId, username, termName, error)

noUIDpurchases = UsageTierPurchase.objects.filter(partnerId="cyverse").filter(partnerUUID__isnull=True)
for purchase in noUIDpurchases:
    username = Credential.objects.filter(partyId=purchase.partyId).first().username
    termName = purchase.tierId.name

    try:
        subscription = client.getSubscriptionTier(username)
        if (subscription['tier'] != termName):
            raise RuntimeError("CyVerse tier name %s and local tier name %s does not match" % (subscription['tier'], termName))
        purchase.partnerUUID = subscription['uuid']
        purchase.save()
        print """
            Synchronizing CyVerse subscription UUID to Phoenix database succeeded.
                Tier Purchase ID: %s
                User Name: %s
                Tier: %s
                Partner UUID: %s
                """ % (purchase.purchaseId, username, termName, subscription['uuid'])
    except RuntimeError as error:
        print """
            Synchronizing CyVerse subscription UUID to Phoenix database failed.
                Tier Purchase ID: %s
                User Name: %s
                Tier: %s
                Error Message: %s
                """ % (purchase.purchaseId, username, termName, error)