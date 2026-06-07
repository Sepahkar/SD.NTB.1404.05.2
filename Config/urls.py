"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

admin.site.site_header = "پنل مدیریت آموزشیار"
admin.site.site_title = "آموزشیار"
admin.site.index_title = "مدیریت داده‌ها"

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'docs/',
        TemplateView.as_view(template_name='RUN_AND_ADMIN_GUIDE.html'),
        name='project-docs',
    ),
    path(
        'docs/setup-theme/',
        TemplateView.as_view(template_name='SETUP_AND_THEME_GUIDE.html'),
        name='setup-theme-guide',
    ),
    path(
        'docs/django-admin/',
        TemplateView.as_view(template_name='DJANGO_ADMIN_COMPLETE_GUIDE.html'),
        name='django-admin-guide',
    ),
]
