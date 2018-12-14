#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from nullservice import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [ 
    url(r'^', views.nullserviceCRUD.as_view(), name='nullservice'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
