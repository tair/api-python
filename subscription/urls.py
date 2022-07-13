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
    url(r'^institutions/$', views.InstitutionSubscription.as_view()),
    url(r'^commercials/$', views.CommercialSubscription.as_view()),
    url(r'^enddate/$', views.EndDate.as_view()),
    url(r'^membership/$', views.Membership.as_view()),
    url(r'^activesubscriptions/(?P<partyId>.+)/$', views.ActiveSubscriptions.as_view()),
    url(r'^allsubscriptions/(?P<partyId>.+)/$', views.AllSubscriptions.as_view()),
    url(r'^consortiums/$', views.ConsortiumSubscriptions.as_view()),
    url(r'^consactsubscriptions/(?P<partyId>.+)/$', views.ConsActSubscriptions.as_view()),
    url(r'^request/$', views.RequestSubscription.as_view()),
    url(r'^renew/$', views.RenewSubscription.as_view()),
    # url(r'^getall/$', views.GetAllSubscription.as_view()),
    url(r'^subscriptionrequest/$', views.SubscriptionRequestCRUD.as_view()),
    url(r'^active/$', views.SubscriptionActiveCRUD.as_view()),

    # Templates
    url(r'^templates/block/$', TemplateView.as_view(template_name="subscription/block.html")),
    # PW-161 https://demoapi.arabidopsis.org/subscriptions/templates/login.html
    # url(r'^templates/login/$', TemplateView.as_view(template_name="subscription/login.html")),

    url(r'^templates/warn/$', TemplateView.as_view(template_name="subscription/warn.html")),
]
urlpatterns = format_suffix_patterns(urlpatterns)
