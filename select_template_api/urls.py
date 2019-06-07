"""CATH SelectTemplate API Urls"""

from django.conf.urls import url
from rest_framework.authtoken import views
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (SelectTemplateTasksCreateView,
                    SelectTemplateTasksStatusView,
                    SelectTemplateTasksResultView,
                    SelectTemplateHitsView,
                    SelectTemplateResolvedHitsView,
                    SelectTemplateAlignmentsView,
                    )

app_name = "select_template_api"

urlpatterns = {
    url(r'^api-token-auth/', views.obtain_auth_token, name="auth_token"),
    url(r'^select-template/$',
        SelectTemplateTasksCreateView.as_view(), name="select_template_create"),
    url(r'^select-template/(?P<uuid>[0-9a-f\-]{32,40})/$',
        SelectTemplateTasksStatusView.as_view(), name="select_template_status"),
    url(r'^select-template/(?P<uuid>[0-9a-f\-]{32,40})/results$',
        SelectTemplateTasksResultView.as_view(), name="select_template_results"),
    url(r'^select-template/(?P<task_uuid>[0-9a-f\-]{32,40})/hits$',
        SelectTemplateHitsView.as_view(), name="select_template_hits"),
    url(r'^select-template/(?P<task_uuid>[0-9a-f\-]{32,40})/resolved_hits$',
        SelectTemplateResolvedHitsView.as_view(), name="select_template_resolved_hits"),
    url(r'^select-template/hit/(?P<hit_uuid>[0-9a-f\-]{32,40})/alignments$',
        SelectTemplateAlignmentsView.as_view(), name="select_template_alignments"),
}

urlpatterns = format_suffix_patterns(urlpatterns)
