#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from accessControl import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^queries/$', views.Queries.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
