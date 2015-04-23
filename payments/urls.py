#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from payments import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.paymentInfo, name='paymentInfo'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
