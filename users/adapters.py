"""
Custom adapter for django-allauth to handle login redirects based on user type.
"""
from allauth.account.adapter import DefaultAccountAdapter
from django.urls import reverse


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

