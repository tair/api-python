#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from ipranges import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^validateip/$', views.validateip, name='validateip'),
    #url(r'^get/$', views.getcookie, name='getcookie'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
