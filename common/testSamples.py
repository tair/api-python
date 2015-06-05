from apikey.models import ApiKey
from partner.models import Partner
import copy

def forcePost(model, pkName, data):
    u = model(**data)
    u.save()
    return u.__dict__[pkName]

class CommonApiKeySample():
    data = {
        'apiKey':'testKey',
    }
    pkName = 'apiKeyId'
    model = ApiKey

    def forcePost(self,data):
        return forcePost(self.model, self.pkName, data)
