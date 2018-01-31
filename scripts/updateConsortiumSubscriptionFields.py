from party.models import Party
from partner.models import Partner
from subscription.models import Subscription
from subscription.serializers import SubscriptionSerializer

from django.db.models import Max

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
                if obj.consortiumStartDate != subscription.startDate\
                    or obj.consortiumEndDate != subscription.endDate\
                    or obj.consortiumId != subscription.partyId:
                    serializer = SubscriptionSerializer(obj, data=updateData, null=True)
                    if serializer.is_valid():
                        serializer.save()


