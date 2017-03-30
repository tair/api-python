from apikey.models import ApiKey
from rest_framework_jwt.utils import jwt_decode_handler
from authentication.models import Credential
from party.models import Party

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
    from authentication.models import Credential
    credentialId = request.GET.get('credentialId')
    secretKey = request.GET.get('secretKey')
    token = None
    if credentialId and secretKey and Credential.validate(credentialId, token, secretKey):
        return True
    return False

def isLoggedIn(request):
    from authentication.models import Credential
    credentialId = request.GET.get('credentialId')
    secretKey = request.GET.get('secretKey')
    token = None
    if credentialId and secretKey and Credential.validate(credentialId, token, secretKey):# and Credential.objects.get(partyId=credentialId).partyId.partyType=='phoenix':
        return True
    return False

def rolePermission(request, roleList):
    if request.META.get('HTTP_AUTHORIZATION'):
        token = request.META.get('HTTP_AUTHORIZATION')
        payload = jwt_decode_handler(token)
        user_id = payload['user_id']
        partyType = ''
        if Credential.objects.all().filter(user_id=user_id).exists():
            partyId = Credential.objects.get(user_id=user_id).partyId.partyId
            partyType = Party.objects.all().get(partyId=partyId).partyType

        for role in roleList:
            if partyType == role:
                return True
    return False
