#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from authentication import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^$', views.listcreateuser.as_view(), name='listcreateuser'),
    url(r'^login/$', views.login, name='login'),
    # PW-161 url(r'^register', views.registerUser, name='register'),
    # PW-123 /credintials/forgot
    url(r'^resetPassword', views.ResetPassword, name='resetPassword'),
    url(r'^resetPassword2', views.ResetPassword2, name='resetPassword2'),
    
]

urlpatterns = format_suffix_patterns(urlpatterns)
