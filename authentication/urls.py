#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from authentication import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^$', views.listcreateuser.as_view(), name='listcreateuser'),
    # PW-161 url(r'^login/$', views.login, name='login'),
    # PW-161 url(r'^register', views.registerUser, name='register'),
    # PW-123 /credintials/forgot
    url(r'^forgot', views.ForgotPassword, name='forgot'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
