"""backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from core.admin import custom_admin_site
from django.urls import path, include
from rest_framework.documentation import include_docs_urls
from django.contrib.auth import views as auth_views
from sales.views import receipt
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='customers')),
    path('sales/receipt/<int:pk>/', receipt, name='receipt'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('admin/', custom_admin_site.urls),
    path(
        'password_reset/',
        auth_views.PasswordResetView.as_view(),
        name='admin_password_reset',
    ),
    path(
        'password_reset/done/',
        auth_views.PasswordResetDoneView.as_view(),
        name='password_reset_done',
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    path(
        'reset/done/',
        auth_views.PasswordResetCompleteView.as_view(),
        name='password_reset_complete',
    ),
    path('core/', include('core.web_urls')),
    path('sales/', include('sales.web_urls')),
    path('system/', include('system_settings.urls')),
    path('resources/sales/', include('sales.resource_urls')),
    path('reports/', include('reports.urls')),
    path('api/core/', include('core.urls')),
    path('api/sales/', include('sales.urls')),
    path('api/auth/', include('djoser.urls')),
    path('api/auth/', include('djoser.urls.jwt')),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('docs/', include_docs_urls(title='MGH API', public=False)),
    path('select2/', include('django_select2.urls'))
]

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns
