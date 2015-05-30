#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from subscription import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUD operations
    url(r'^transactions/$', views.SubscriptionTransactionCRUD.as_view()),
    url(r'^$', views.SubscriptionCRUD.as_view()),

    # Specific queries about subscription
    url(r'^(?P<pk>[0-9.]+)/renewal/$', views.SubscriptionRenewal.as_view()),
    url(r'^active/$', views.SubscriptionsActive.as_view()),
    url(r'^payments/$', views.SubscriptionsPayment.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
