from collections import namedtuple

from subscription.models import Subscription

INSTITUTIONAL_PARTY_TYPES = ('organization', 'consortium')

Expiring = namedtuple('Expiring', [
    'name',
    'start_date',
    'end_date',
])


def between(partners, start, end):
    return [
        Expiring(
            name=s.partyId.name,
            start_date=s.startDate,
            end_date=s.endDate,
        )
        for s in Subscription.endingBetween(start, end).filter(
            partnerId__in=partners,
            partyId__partyType__in=INSTITUTIONAL_PARTY_TYPES,
        ).select_related('partyId').order_by('endDate')
    ]
