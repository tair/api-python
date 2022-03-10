from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from django.middleware.csrf import get_token
from django.http import HttpResponse
import json
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
# Create your views here.

#@ensure_csrf_cookie
@api_view(('get',))
@permission_classes((AllowAny,))
def getcookie(request):
	response = HttpResponse(json.dumps({"message": "success", "csrftoken": get_token(request)}), status=200) 
	#response.set_cookie("csrftoken", get_token(request), domain=".steveatgetexp.com")
	return response
