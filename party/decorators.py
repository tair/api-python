from models import Party

# This decorator is used to update hasIpRange field of Party after a parties/ipranges/ POST or DELETE request made
def updateHasIpRange(func):
    def wrapper(request, format=None):
        func(request, format=None)
        party = Party.objects.get(partyId=request.GET['partyId'])
        party.hasIpRange = True if party.iprange_set.all() else False
        party.save()

    return wrapper