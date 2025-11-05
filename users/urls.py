from django.urls import path
from .views import register_view, login_view, logout_view, employer_onboarding_view

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('employer-onboarding/', employer_onboarding_view, name='employer-onboarding'),
]
