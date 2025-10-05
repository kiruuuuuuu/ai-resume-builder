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
]

