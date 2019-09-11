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
        updateData = {}
        # find active consortium subscriptions with largest end date
        activeSubscription = Subscription.objects.all().filter(partyId__in=consortiumIdList)\
            .filter(partnerId=partner)\
            .filter(startDate__lte=timezone.now())\
            .filter(endDate__gte=timezone.now()) \
            .order_by('-endDate').first()
        # if exists set to update data
        if activeSubscription:
            consortiumSubscribed = True
            updateData['consortiumStartDate'] = activeSubscription.startDate
            updateData['consortiumEndDate'] = activeSubscription.endDate
            updateData['consortiumId'] = activeSubscription.partyId
        # if not exist, find all consortium subscriptions with largest end date
        else:
            subscription = Subscription.objects.all().filter(partyId__in=consortiumIdList)\
                .filter(partnerId=partner)\
                .order_by('-endDate').first()
            # if exists set to update data
            if subscription:
                consortiumSubscribed = True
                updateData['consortiumStartDate'] = subscription.startDate
                updateData['consortiumEndDate'] = subscription.endDate
                updateData['consortiumId'] = subscription.partyId
            else:
                consortiumSubscribed = False
                updateData['consortiumStartDate'] = None
                updateData['consortiumEndDate'] = None
                updateData['consortiumId'] = None

        created = False
        obj = None
        if consortiumSubscribed:
            # if the obj doesn't exist then create
            obj, created = Subscription.objects.get_or_create(
                partnerId=partner,
                partyId=institution,
                defaults=updateData,
            )
        else:
            try:
                obj = Subscription.objects.get(partyId=institution, partnerId=partner)
            except Subscription.DoesNotExist:
                continue
        # if the obj exists then update
        if not created:
            for k, v in updateData.items():
                if getattr(obj, k) != v:
                    setattr(obj, k, v)
                    obj.save()

        if not obj.startDate and not obj.endDate and not obj.consortiumStartDate and not obj.consortiumEndDate and not obj.consortiumId:
            obj.delete()


