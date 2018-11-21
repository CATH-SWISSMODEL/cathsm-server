"""Main Urls"""

from django.conf.urls import url
from . import views

app_name = "frontend"

urlpatterns = [
    url(r'^', views.FrontendAppView.as_view()),
]
