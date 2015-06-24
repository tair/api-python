#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.

from django.conf.urls import url
from subscription import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.views.generic import TemplateView

urlpatterns = [
    # Basic CRUD operations
    url(r'^transactions/$', views.SubscriptionTransactionCRUD.as_view()),
    url(r'^activationCodes/$', views.ActivationCodeCRUD.as_view()),
    url(r'^$', views.SubscriptionCRUD.as_view()),

    # Specific queries about subscription
    url(r'^(?P<pk>[0-9.]+)/renewal/$', views.SubscriptionRenewal.as_view()),
    url(r'^payments/$', views.SubscriptionsPayment.as_view()),

    # Templates
    url(r'^templates/block/$', TemplateView.as_view(template_name="subscription/block.html")),
    url(r'^templates/login/$', TemplateView.as_view(template_name="subscription/login.html")),
    url(r'^templates/warn/$', TemplateView.as_view(template_name="subscription/warn.html")),
]
urlpatterns = format_suffix_patterns(urlpatterns)
