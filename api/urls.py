# api/urls.py

from django.conf.urls import url, include
from .views import SelectTemplateTaskCreateView, SelectTemplateTaskDetailsView
from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = {
    url(r'^select-template/$', SelectTemplateTaskCreateView.as_view(), name="create_selecttemplate"),
    url(r'^select-template/(?P<pk>[0-9]+)/$', SelectTemplateTaskDetailsView.as_view(), name="details_selecttemplate"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
