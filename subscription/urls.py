#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from subscription import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^parties/$', views.Parties.as_view()),
    url(r'^payments/(?P<pk>[0-9.]+)/$', views.PaymentsDetail.as_view()),
    url(r'^payments/$', views.Payments.as_view()),
    url(r'^ipranges/(?P<pk>[0-9.]+)/$', views.IpRangesDetail.as_view()),
    url(r'^ipranges/$', views.IpRanges.as_view()),
    url(r'^active/$', views.SubscriptionsActive.as_view()),
    url(r'^(?P<pk>[0-9.]+)/payments/', views.SubscriptionsPayments.as_view()),
    url(r'^(?P<pk>[0-9.]+)/prices/', views.SubscriptionsPrices.as_view()),
    url(r'^$', views.Subscriptions.as_view()),
    url(r'^(?P<pk>[0-9.]+)/$', views.SubscriptionsDetail.as_view()),
    url(r'^terms/(?P<pk>[0-9.]+)/$', views.TermsDetail.as_view()),
    url(r'^terms/$', views.Terms.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
