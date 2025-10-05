from django.urls import path
from .views import register_view, login_view, logout_view, edit_personal_details

app_name = 'users'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('profile/edit/', edit_personal_details, name='edit-personal-details'),
]

