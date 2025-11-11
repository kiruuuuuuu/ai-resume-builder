"""
Custom adapter for django-allauth to handle login redirects based on user type.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.urls import reverse
from .models import JobSeekerProfile, EmployerProfile


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter that redirects users to appropriate pages after login
    based on their user type.
    """
    
    def get_login_redirect_url(self, request):
        """
        Override the default login redirect URL to redirect based on user type.
        """
        user = request.user
        
        # Check if user is authenticated and has a user_type
        if user.is_authenticated and hasattr(user, 'user_type'):
            if user.user_type == 'job_seeker':
                return reverse('resumes:resume-builder')
            elif user.user_type == 'employer':
                return reverse('jobs:my-jobs')
        
        # Fallback to default behavior
        return super().get_login_redirect_url(request)
    
    def get_signup_redirect_url(self, request):
        """
        Override the default signup redirect URL to redirect based on user type.
        """
        user = request.user
        
        # Check if user is authenticated and has a user_type
        if user.is_authenticated and hasattr(user, 'user_type'):
            if user.user_type == 'job_seeker':
                return reverse('resumes:resume-builder')
            elif user.user_type == 'employer':
                return reverse('users:employer-onboarding')
        
        # Fallback to default behavior
        return super().get_signup_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account signups to handle user_type assignment.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before a social account is logged in.
        If the user doesn't exist yet, we'll create them with default user_type.
        """
        # If user is already authenticated, just connect the account
        if request.user.is_authenticated:
            return
        
        # If social account already exists, nothing to do
        if sociallogin.is_existing:
            return
        
        # For new users, we'll set default user_type in save_user
        pass
    
    def save_user(self, request, sociallogin, form=None):
        """
        Override to set default user_type for social signups.
        Default to 'job_seeker' for social signups (can be changed later).
        """
        user = super().save_user(request, sociallogin, form)
        
        # Set default user_type for social signups (default to job_seeker)
        if not user.user_type:
            user.user_type = 'job_seeker'
            user.save()
        
        # Create profile based on user_type
        if user.user_type == 'job_seeker':
            JobSeekerProfile.objects.get_or_create(user=user)
        elif user.user_type == 'employer':
            EmployerProfile.objects.get_or_create(user=user)
        
        return user

