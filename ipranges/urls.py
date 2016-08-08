#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from cookies import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^validIpAddress/$', views.validateip, name='validateip'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
