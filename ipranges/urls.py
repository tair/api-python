#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from ipranges import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^validateip/$', views.validateip.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
