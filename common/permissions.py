from apikey.models import ApiKey

class ApiKeyPermission():
    def has_permission(self, request, view):
        if hasattr(view, 'requireApiKey') and view.requireApiKey == False:
            # view specifically declared not require ApiKey
            return True
        # uncomment the following line and comment the line afterward
        # to enable cookie to pass in apiKey
        apiKey = view.request.COOKIES.get('apiKey')

        if apiKey == None:
            return False
        if (ApiKey.objects.all().filter(apiKey=apiKey).exists()):
            return True
        return False

    def has_object_permission(self, request, view, obj):
        return True

def isPhoenix(request):
    from authentication.models import Credential
    partyId = request.GET.get('partyId')
    secretKey = request.GET.get('secret_key')
    if partyId and secretKey and Credential.validate(partyId, secretKey):
        return True
    return False

def isLoggedIn(request):
    from authentication.models import Credential
    partyId = request.GET.get('partyId')
    secretKey = request.GET.get('secret_key')
    if partyId and secretKey and Credential.validate(partyId, secretKey):# and Credential.objects.get(partyId=partyId).partyId.partyType=='phoenix':
        return True
    return False
