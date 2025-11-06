"""
URL configuration for core project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from pages.views import home_view

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_view, name="home"),
    
    # django-allauth URLs (must be before users.urls to override login)
    path("accounts/", include("allauth.urls")),
    
    # Include app-specific URLs. The namespace is now defined in each app's urls.py
    path("users/", include("users.urls")),
    path("resumes/", include("resumes.urls")),
    path("jobs/", include("jobs.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

