#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from authorization import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^accessTypes/$', views.AccessTypeCRUD.as_view()),
    url(r'^accessRules/$', views.AccessRuleCRUD.as_view()),
    url(r'^patterns/$', views.URIAccess.as_view()),

    # Specific queries
    url(r'^access/$', views.Access.as_view()),
    url(r'^subscriptions/$', views.SubscriptionsAccess.as_view()),
    url(r'^authentications/$', views.AuthenticationsAccess.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
