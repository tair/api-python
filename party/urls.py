#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from party import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^countries/$', views.CountryView.as_view()),
    url(r'^organizations/$', views.OrganizationView.as_view()),#PW-265

    url(r'^ipranges/$', views.IpRangeCRUD.as_view()),
    #https://demoapi.arabidopsis.org/parties/?partyId=31627&credentialId=33197&secretKey=kZ5yK8hdSbncXwD4%2F2DJOxqFUds%3D
    url(r'^$', views.PartyCRUD.as_view()),

    # Specific queries
    url(r'^usage/$', views.Usage.as_view()),
    url(r'^consortiuminstitutions/(?P<consortiumId>[0-9]+)/$', views.ConsortiumInstitutions.as_view()),
    url(r'^consortiums/$', views.ConsortiumCRUD.as_view()),
    #https://demoapi.arabidopsis.org/parties/institutions/?partyId=31627&credentialId=33197&secretKey=kZ5yK8hdSbncXwD4%2F2DJOxqFUds%3D
    url(r'^institutions/$', views.InstitutionCRUD.as_view()),#PW-161
    url(r'^affiliations/$', views.AffiliationCRUD.as_view()),

    #PW-277 - accept IP, returns organization
    #https://demoapi.arabidopsis.org/parties/institutions/?IP=31627&credentialId=33197&secretKey=kZ5yK8hdSbncXwD4%2F2DJOxqFUds%3D
    url(r'^org/$', views.PartyOrgCRUD.as_view()),
    url(r'^orgstatus/$', views.PartyOrgStatusView.as_view()),

]
urlpatterns = format_suffix_patterns(urlpatterns)
