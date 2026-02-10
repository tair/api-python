#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from authentication import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^$', views.listcreateuser.as_view(), name='listcreateuser'),
    url(r'^login/$', views.login, name='login'),
    url(r'^resetPwd/$', views.resetPwd, name='resetPwd'),
    url(r'^profile/$', views.profile.as_view(), name='profile'),
    url(r'^getUsernames/$', views.getUsernameCRUD.as_view(), name='getUsernames'),
    url(r'^checkAccountExists$', views.checkAccountExists, name='checkAccountExists'),
    url(r'^checkOrcid/$', views.checkOrcid, name='checkOrcid'),
    url(r'^getUserIdentifierByOrcid/$', views.getUserIdentifierByOrcid, name='getUserIdentifierByOrcid'),
    url(r'^addOrcidCredentials/$', views.addOrcidCredentials, name='addOrcidCredentials'),
    url(r'^authenticateOrcid/$', views.authenticateOrcid, name='authenticateOrcid'),
    url(r'^unlinkOrcid/$', views.unlinkOrcid, name='unlinkOrcid'),
    url(r'^deactivate/$', views.deactivateUser.as_view(), name='deactivateUser'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
