#Copyright 2015 Phoenix Bioinformatics Corporation. All rights reserved.




from django.conf.urls import url
from partner import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    # Basic CRUDs
    url(r'^descriptions/$', views.SubscriptionDescriptionCRUD.as_view()),
    url(r'^descriptionItems/$', views.SubscriptionDescriptionItemCRUD.as_view()),
    url(r'^patterns/$', views.PartnerPatternCRUD.as_view()),
    url(r'^terms/$', views.TermsCRUD.as_view()),
    url(r'^$', views.PartnerCRUD.as_view()),
]
urlpatterns = format_suffix_patterns(urlpatterns)
