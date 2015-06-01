#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from loggingapp import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^page-views/$', views.PageViewCRUD.as_view()),
    url(r'^sessions/counts/$', views.SessionCountView.as_view()),
]

urlpatterns = format_suffix_patterns(urlpatterns)
