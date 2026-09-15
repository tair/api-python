from collections import namedtuple

from subscription.models import Subscription

# What the report covers. Both are fixed scope rather than caller's business:
# the digest goes to TAIR's team, and institutional renewals are the only ones
# negotiated offline. Parameterise either the day a second consumer wants it.
PARTNERS = ('tair',)
INSTITUTIONAL_PARTY_TYPES = ('organization', 'consortium')

Expiring = namedtuple('Expiring', [
    'name',
    'start_date',
    'end_date',
])


def between(start, end):
    return [
        Expiring(
            name=s.partyId.name,
            start_date=s.startDate,
            end_date=s.endDate,
        )
        for s in Subscription.endingBetween(start, end).filter(
            partnerId__in=PARTNERS,
            partyId__partyType__in=INSTITUTIONAL_PARTY_TYPES,
        ).select_related('partyId').order_by('endDate')
    ]
