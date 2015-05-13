#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from partner import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^patterns/$', views.PartnerPatternsList.as_view()),
    url(r'^patterns/(?P<pk>[0-9.]+)/$', views.PartnerPatternsDetail.as_view()),
    url(r'^terms/$', views.TermsList.as_view()),
    url(r'^terms/(?P<pk>[0-9.]+)/$', views.TermsDetail.as_view()),
    url(r'^$', views.PartnerList.as_view()),
    url(r'^(?P<pk>[0-9a-zA-Z.]+)/$', views.PartnerDetail.as_view()),

    # Specific queries
    url(r'^terms/queries/', views.TermsQueries.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
