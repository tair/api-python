#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers
from rest_framework_jwt.views import obtain_jwt_token

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
    url(r'^credentials/', include('authentication.urls', namespace="authentication")),
    url(r'^apikeys/', include('apikey.urls')),
    url(r'^cookies/', include('cookies.urls')),
    url(r'^api-token-auth/', obtain_jwt_token),
    url(r'^ipranges/', include('ipranges.urls')),
)
