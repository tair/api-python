from django.http import HttpResponse
from common.views import GenericCRUDView
# Create your views here.

class nullserviceCRUD(GenericCRUDView):
    def get(self, request, format=None):
        return HttpResponse('nullack');