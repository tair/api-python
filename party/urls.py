#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from party import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^organizations/$', views.OrganizationCRUD.as_view()),
    url(r'^ipranges/$', views.IpRangeCRUD.as_view()),
    url(r'^$', views.PartyCRUD.as_view()),

    # Specific queries
]
urlpatterns = format_suffix_patterns(urlpatterns)
