#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from subscription import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^parties/$', views.PartiesList.as_view()),
    url(r'^parties/(?P<pk>[0-9.]+)/$', views.PartiesDetail.as_view()),
    url(r'^transactions/$', views.SubscriptionTransactionsList.as_view()),
    url(r'^transactions/(?P<pk>[0-9.]+)/$', views.SubscriptionTransactionsDetail.as_view()),
    url(r'^ipranges/$', views.IpRangesList.as_view()),
    url(r'^ipranges/(?P<pk>[0-9.]+)/$', views.IpRangesDetail.as_view()),
    url(r'^$', views.SubscriptionsList.as_view()),
    url(r'^(?P<pk>[0-9.]+)/$', views.SubscriptionsDetail.as_view()),
    url(r'^(?P<pk>[0-9.]+)/renewal/$', views.SubscriptionRenewal.as_view()),

    # Specific queries about subscription
    url(r'^active/$', views.SubscriptionsActive.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
