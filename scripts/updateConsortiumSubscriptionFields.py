import django
import os

os.sys.path.append('../')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paywall2.settings')
django.setup()

from party.models import Party
from partner.models import Partner
from subscription.models import Subscription

from django.utils import timezone

institutions = Party.objects.prefetch_related('consortiums').filter(partyType='organization')
partners = Partner.objects.all()

for institution in institutions:
    for partner in partners:
        consortiumIdList = institution.consortiums.all().values_list('partyId', flat=True)
        subscription = Subscription.objects.all().filter(partyId__in=consortiumIdList)\
            .filter(partnerId=partner)\
            .filter(startDate__lte=timezone.now())\
            .filter(endDate__gte=timezone.now()) \
            .order_by('-endDate').first()
        # if any consortium has an active subscription for the certain partner
        if subscription:
            updateData = {}
            updateData['consortiumStartDate'] = subscription.startDate
            updateData['consortiumEndDate'] = subscription.endDate
            updateData['consortiumId'] = subscription.partyId
            # if the obj doesn't exist then create
            obj, created = Subscription.objects.get_or_create(
                partnerId=partner,
                partyId=institution,
                defaults=updateData,
            )
            # if the obj exists then update
            if not created:
                for k, v in updateData.iteritems():
                    if getattr(obj, k) != v:
                        setattr(obj, k, v)


