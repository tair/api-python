#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from party.models import Party, IpRange
from party.serializers import PartySerializer, IpRangeSerializer

from common.views import GenericCRUDView

# top level: /parties/

# Basic CRUD operation for Party and IpRange

# /
class PartyCRUD(GenericCRUDView):
    queryset = Party.objects.all()
    serializer_class = PartySerializer

# /ipranges/
class IpRangeCRUD(GenericCRUDView):
    queryset = IpRange.objects.all()
    serializer_class = IpRangeSerializer


#------------------- End of Basic CRUD operations --------------
