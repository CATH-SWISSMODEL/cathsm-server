"""cathapi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf.urls import url, include
from rest_framework import permissions, routers
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator

class CustomOpenAPISchemaGenerator(OpenAPISchemaGenerator):
    def get_schema(self, *args, **kwargs):
        schema = super().get_schema(*args, **kwargs)
        schema.basePath = '/api' # API prefix
        return schema

SelectTemplateApi = get_schema_view(
    openapi.Info(
        title="CATH-SWISSMODEL API",
        default_version='v0.0.1',
        description=("Select a template structure on which to model "
                     "the 3D coordinates of a given protein sequence."),
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="i.sillitoe@ucl.ac.uk"),
        license=openapi.License(name="BSD License"),
    ),
    validators=['flex', 'ssv'],
    public=True,
    generator_class=CustomOpenAPISchemaGenerator,
    permission_classes=(permissions.AllowAny,),
)

# Routers provide an easy way of automatically determining the URL conf.
ROUTER = routers.DefaultRouter()

urlpatterns = [
    url(r'^swagger(?P<format>\.json|\.yaml)$',
        SelectTemplateApi.without_ui(cache_timeout=None), name='schema-json'),
    url(r'^swagger/$', SelectTemplateApi.with_ui('swagger', cache_timeout=None), name='schema-swagger-ui'),
    url(r'^redoc/$', SelectTemplateApi.with_ui('redoc', cache_timeout=None), name='schema-redoc'),
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('select_template_api.urls')),
#    url(r'^api/', include(ROUTER.urls)),
    url(r'^frontend/', include('frontend.urls')),
]
