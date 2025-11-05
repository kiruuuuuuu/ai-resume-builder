from django.urls import path
from .views import (
    post_job_view,
    job_list_view,
    job_detail_view,
    apply_for_job_view,
    employer_jobs_view,
    view_applicants_view,
    mark_notification_as_read_view,
    edit_job_view,
    my_applications_view,
    update_application_status,
    schedule_interview_view,
    respond_to_interview_view,
    view_applicant_resume,
    generate_job_description_api,
    generate_applicant_summary_api,
    generate_interview_prep_api,
    interview_prep_view,
    company_profile_view,
    download_interview_calendar,
    job_stats_view,
)

app_name = 'jobs'

urlpatterns = [
    path('post/', post_job_view, name='post-job'),
    path('<int:job_id>/edit/', edit_job_view, name='edit-job'),
    path('', job_list_view, name='job-list'),
    path('<int:job_id>/', job_detail_view, name='job-detail'),
    path('<int:job_id>/apply/', apply_for_job_view, name='apply-for-job'),
    path('my-jobs/', employer_jobs_view, name='my-jobs'),
    path('<int:job_id>/applicants/', view_applicants_view, name='view-applicants'),
    path('applicant/<int:application_id>/resume/', view_applicant_resume, name='view-applicant-resume'),
    path('my-applications/', my_applications_view, name='my-applications'),
    path('application/<int:application_id>/update/', update_application_status, name='update-application-status'),
    path('application/<int:application_id>/schedule/', schedule_interview_view, name='schedule-interview'),
    path('interview/<int:interview_id>/respond/', respond_to_interview_view, name='respond-to-interview'),
    path('notifications/<int:notification_id>/read/', mark_notification_as_read_view, name='mark-notification-read'),
    path('api/generate-job-description/', generate_job_description_api, name='generate-job-description'),
    path('api/generate-applicant-summary/', generate_applicant_summary_api, name='generate-applicant-summary'),
    path('api/generate-interview-prep/', generate_interview_prep_api, name='generate-interview-prep'),
    path('application/<int:application_id>/interview-prep/', interview_prep_view, name='interview-prep'),
    path('company/<int:employer_id>/', company_profile_view, name='company-profile'),
    path('interview/<int:interview_id>/download-calendar/', download_interview_calendar, name='download-interview-calendar'),
    path('<int:job_id>/stats/', job_stats_view, name='job-stats'),
]

