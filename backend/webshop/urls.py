"""webshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

api_info = openapi.Info(
    title="Webshop API",
    default_version='v1',
    description="Webshop API Description",
    terms_of_service="https://badasswebshop.com/terms",
    contact=openapi.Contact(email="mbranko@uns.ac.rs"),
    license=openapi.License(name="MIT License"),
)

schema_view = get_schema_view(
    openapi.Info(
        title="Webshop API",
        default_version='v1',
        description="Webshop API Description",
        terms_of_service="https://badasswebshop.com/terms",
        contact=openapi.Contact(email="mbranko@uns.ac.rs"),
        license=openapi.License(name="MIT License"),
    ),
    public=False,
    permission_classes=(permissions.IsAdminUser,),
)


urlpatterns = [
    # dokumentacija za API
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # admin sajt
    path('admin/', admin.site.urls),

    # JWT autentifikacija
    path('api/token-auth/', obtain_jwt_token),
    path('api/token-refresh/', refresh_jwt_token),

    # autentifikacija za Django REST Framework
    path('api/auth/', include('rest_framework.urls')),

    # mainshop REST API
    path('api/', include('mainshop.urls_api', namespace='mainshop_api')),

    # mainshop stranice
    path('', include('mainshop.urls', namespace='mainshop')),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path(r'__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
