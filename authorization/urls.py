#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from authorization import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^accessTypes/$', views.AccessTypesList.as_view()),
    url(r'^accessTypes/(?P<pk>[0-9]+)/$', views.AccessTypesDetail.as_view()),
    url(r'^accessRules/$', views.AccessRulesList.as_view()),
    url(r'^accessRules/(?P<pk>[0-9]+)/$', views.AccessRulesDetail.as_view()),
    url(r'^patterns/$', views.UriPatternList.as_view()),
    url(r'^patterns/(?P<pk>[0-9]+)/$', views.UriPatternDetail.as_view()),

    # Specific queries
    url(r'^access/$', views.Access.as_view()),
    url(r'^subscriptions/$', views.SubscriptionsAccess.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
