#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from apikey import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^$', views.ApiKeyCRUD.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
