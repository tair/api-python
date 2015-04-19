#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.





from django.conf.urls import patterns, include, url
from django.contrib import admin
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = patterns('',
    url(r'^', include('proxy.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include(router.urls)),
)
