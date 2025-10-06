from django.urls import path
from .views import (
    resume_dashboard_view,
    resume_builder_view,
    upload_resume_view,
    validate_resume_data_view,
    enhance_description_api,
    download_resume_pdf,
    delete_item,
    edit_item,
    parsing_progress_view,
    check_parsing_status_view,
    check_score_status_view, # --- THE FIX IS HERE ---
)

app_name = 'resumes'

urlpatterns = [
    path('dashboard/', resume_dashboard_view, name='resume-dashboard'),
    path('builder/', resume_builder_view, name='resume-builder'),
    path('upload/', upload_resume_view, name='resume-upload'),
    path('validate/', validate_resume_data_view, name='resume-validate'),
    path('<int:resume_id>/download/<str:template_name>/', download_resume_pdf, name='download-resume-pdf'),
    path('api/<str:model_name>/<int:pk>/delete/', delete_item, name='delete-item'),
    path('<str:model_name>/<int:pk>/edit/', edit_item, name='edit-item'),
    path('api/enhance-description/', enhance_description_api, name='enhance-api'),
    path('parsing-progress/', parsing_progress_view, name='parsing-progress'),
    path('check-parsing-status/', check_parsing_status_view, name='check-parsing-status'),
    # --- THE FIX IS HERE: New URL for checking score status ---
    path('api/check-score-status/<int:resume_id>/', check_score_status_view, name='check-score-status'),
]
