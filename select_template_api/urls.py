"""CATH SelectTemplate API Urls"""

from django.conf.urls import url
from rest_framework.authtoken import views
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (SelectTemplateTaskCreateView, SelectTemplateTaskStatusView, 
    SelectTemplateTaskResultsView)

app_name = "select_template_api"

urlpatterns = {
    url(r'^api-auth-token/', views.obtain_auth_token, name="auth_token"),
    url(r'^select-template/$',
        SelectTemplateTaskCreateView.as_view(), name="create_selecttemplate"),
    url(r'^select-template/(?P<uuid>[0-9a-f\-]{32,40})/$',
        SelectTemplateTaskStatusView.as_view(), name="status_selecttemplate"),
    url(r'^select-template/(?P<uuid>[0-9a-f\-]{32,40})/results$',
        SelectTemplateTaskResultsView.as_view(), name="results_selecttemplate"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
