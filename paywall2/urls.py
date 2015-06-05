#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
    url(r'^meters/', include('metering.urls')),
    url(r'^parties/', include('party.urls')),
    url(r'^subscriptions/', include('subscription.urls')),
    url(r'^authorizations/', include('authorization.urls')),
    url(r'^partners/', include('partner.urls')),
    url(r'^session-logs/', include('loggingapp.urls')),
    url(r'^users/', include('authentication.urls', namespace="authentication")),
    url(r'^apikeys/', include('apikey.urls')),
)
