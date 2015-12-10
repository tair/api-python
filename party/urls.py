#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from party import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^countries/$', views.CountryView.as_view()),
    url(r'^organizations/$', views.OrganizationView.as_view()),
    url(r'^ipranges/$', views.IpRangeCRUD.as_view()),
    url(r'^$', views.PartyCRUD.as_view()),

    # Specific queries
    url(r'^usage/$', views.Usage.as_view()),
    url(r'^consortiuminstitutions/(?P<consortiumId>[0-9]+)/$', views.ConsortiumInstitutions.as_view()),
    url(r'^consortiums/$', views.ConsortiumCRUD.as_view()),
    url(r'^affiliations/$', views.AffiliationCRUD.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
