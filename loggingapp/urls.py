#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from loggingapp import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^sessions/$', views.SessionListCreate.as_view()),
    #url(r'^sessions/create/$', views.SessionCreate.as_view()),
    #url(r'^page-views/create/$', views.PageViewCreate.as_view()),
    url(r'^page-views/$', views.PageViewListCreate.as_view()),
#    url(r'')
]

urlpatterns = format_suffix_patterns(urlpatterns)
