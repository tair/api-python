#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from metering import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.ipList.as_view()),
    url(r'^ip/$', views.ipList.as_view()),
    url(r'^ip/(?P<pk>[0-9.]+)/$', views.ipDetail.as_view()),
    url(r'^ip/(?P<ip>[0-9.]+)/increment/$', views.increment.as_view(), name='increment'),
    #url(r'^ip/(?P<ip>[0-9.]+)/atWarningLimit/$', views.exceedsWarningLimit.as_view()),
    #url(r'^ip/(?P<ip>[0-9.]+)/atMeteringLimit/$', views.exceedsMeteringLimit.as_view()),
    url(r'^ip/(?P<ip>[0-9.]+)/limit/$', views.check_limit.as_view(), name='check_limit'),
    url(r'^limits/warningLimit/$', views.warningLimit.as_view()),
    url(r'^limits/meteringLimit/$', views.meteringLimit.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
