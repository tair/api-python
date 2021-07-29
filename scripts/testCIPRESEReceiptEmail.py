# invoke by
# echo "import scripts.testCIPRESEmailReceipt" | ./manage.py shell
import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()
from subscription.controls import PaymentControl
from partner.models import SubscriptionTerm, Partner

msg = "To access CIPRES resources, please visit phylo.org and log in using your CIPRES user account."
purchaseId = 145
partnerObj = Partner.objects.get(partnerId='cipres')
termObj = SubscriptionTerm.objects.get(subscriptionTermId=20)
emailAddress = 'xingguo.chen@arabidopsis.org'
firstname = 'Ondrej'
lastname = 'Mikula'
priceToCharge = 100
institute = 'Institute of Vertebrate Biology - ASCR'
transactionId = 'ch_1JGRw9DbkoAs09FVhJp7U22l'
vat = ''
try:
    PaymentControl.sendCIPRESEmail(msg, purchaseId, termObj, partnerObj, emailAddress, firstname, lastname, priceToCharge, institute, transactionId, vat)    
except Exception, e:
    print "Unexpected exception: %s" % (e)
