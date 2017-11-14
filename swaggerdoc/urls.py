from django.conf.urls import url
from . import views
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    url(r'^$', views.schema_view, name='schema_view'),
]
urlpatterns = format_suffix_patterns(urlpatterns)