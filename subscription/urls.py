#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from subscription import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^parties/$', views.PartiesList.as_view()),
    url(r'^parties/(?P<pk>[0-9.]+)/$', views.PartiesDetail.as_view()),
    url(r'^ipranges/$', views.IpRangesList.as_view()),
    url(r'^ipranges/(?P<pk>[0-9.]+)/$', views.IpRangesDetail.as_view()),
    url(r'^$', views.SubscriptionStatesList.as_view()),
    url(r'^(?P<pk>[0-9.]+)/$', views.SubscriptionStatesDetail.as_view()),
    url(r'^terms/$', views.TermsList.as_view()),
    url(r'^terms/(?P<pk>[0-9.]+)/$', views.TermsDetail.as_view()),

    # Specific queries about subscription
    url(r'^terms/queries/', views.TermsQueries.as_view()),
    url(r'^active/$', views.SubscriptionsActive.as_view()),
    url(r'^(?P<pk>[0-9.]+)/prices/', views.SubscriptionsPrices.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
