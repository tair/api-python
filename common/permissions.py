from apikey.models import ApiKey
from authentication.models import Credential

class ApiKeyPermission():
    @staticmethod
    def has_permission(request, view):
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
    credentialId = request.GET.get('credentialId')
    secretKey = request.GET.get('secretKey')
    if credentialId and secretKey and Credential.validate(credentialId, secretKey):
        return True
    return False

def isLoggedIn(request):
    credentialId = request.GET.get('credentialId')
    secretKey = request.GET.get('secretKey')
    if credentialId and secretKey and Credential.validate(credentialId, secretKey):# and Credential.objects.get(partyId=credentialId).partyId.partyType=='phoenix':
        return True
    return False
