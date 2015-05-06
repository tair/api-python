#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from partner import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^$', views.PartnerList.as_view()),
    url(r'^(?P<pk>[0-9a-zA-Z.]+)/$', views.PartnerDetail.as_view()),

    # Specific queries
]
urlpatterns = format_suffix_patterns(urlpatterns)
