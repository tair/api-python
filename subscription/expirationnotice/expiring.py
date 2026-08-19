from collections import namedtuple

from subscription.models import Subscription

INSTITUTIONAL_PARTY_TYPES = ('organization', 'consortium')

Expiring = namedtuple('Expiring', [
    'partner_id',
    'party_type',
    'name',
    'end_date',
])


def between(partners, start, end):
    return [
        Expiring(
            partner_id=s.partnerId_id,
            party_type=s.partyId.partyType,
            name=s.partyId.name,
            end_date=s.endDate,
        )
        for s in Subscription.endingBetween(start, end).filter(
            partnerId__in=partners,
            partyId__partyType__in=INSTITUTIONAL_PARTY_TYPES,
        ).select_related('partyId').order_by('endDate')
    ]
