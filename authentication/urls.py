#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from authentication import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^$', views.listcreateuser.as_view(), name='listcreateuser'),
    url(r'^login/$', views.login, name='login'),
    #url(r'^loginVerify/$', views.loginVerify, name='loginVerify'),
    url(r'^register', views.registerUser, name='register'),
    #url(r'^adduser', views.adduser.as_view(), name='adduser'),
    #url(r'^googleLogin/$', views.googleLogin, name='googleLogin'),
    #url(r'^googleVerify/$', views.googleVerify, name='googleVerify'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
