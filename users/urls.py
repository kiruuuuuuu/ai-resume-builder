from django.urls import path
from .views import register_view, login_view, logout_view, employer_onboarding_view, edit_profile_view, admin_login_view, admin_dashboard_view, admin_bug_detail_view

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('employer-onboarding/', employer_onboarding_view, name='employer-onboarding'),
    path('edit-profile/', edit_profile_view, name='edit-profile'),
    # Admin routes
    path('admin-login/', admin_login_view, name='admin-login'),
    path('admin-dashboard/', admin_dashboard_view, name='admin-dashboard'),
    path('admin-dashboard/bugs/<int:bug_id>/', admin_bug_detail_view, name='admin-bug-detail'),
]
