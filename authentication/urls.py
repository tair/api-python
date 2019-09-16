#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from authentication import views
from rest_framework.urlpatterns import format_suffix_patterns

app_name = 'authentication'
urlpatterns = [ 
    url(r'^$', views.listcreateuser.as_view(), name='listcreateuser'),
    url(r'^login/$', views.login, name='login'),
    url(r'^resetPwd/$', views.resetPwd, name='resetPwd'),
    url(r'^profile/$', views.profile.as_view(), name='profile'),
    url(r'^getUsernames/$', views.getUsernameCRUD.as_view(), name='getUsernames'),
    url(r'^checkAccountExists$', views.checkAccountExists, name='checkAccountExists'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
