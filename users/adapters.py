"""
Custom adapter for django-allauth to handle login redirects based on user type.
"""
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.utils import user_email
from allauth.exceptions import ImmediateHttpResponse
from django.urls import reverse
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth import get_user_model
from .models import JobSeekerProfile, EmployerProfile

User = get_user_model()


class CustomAccountAdapter(DefaultAccountAdapter):
    """
    Custom adapter that redirects users to appropriate pages after login
    based on their user type.
    """
    
    def get_login_redirect_url(self, request):
        """
        Override the default login redirect URL to redirect based on user type.
        For new social signups, redirect to dashboard if they don't have a resume yet.
        """
        user = request.user
        
        # Check if user is authenticated and has a user_type
        if user.is_authenticated and hasattr(user, 'user_type'):
            if user.user_type == 'job_seeker':
                # Check if this is a new user (first login via social) without a resume
                try:
                    profile = user.jobseekerprofile
                    from resumes.models import Resume
                    # Check if user has any resume
                    if not Resume.objects.filter(profile=profile).exists():
                        # New user - redirect to dashboard to show upload/build options
                        return reverse('resumes:resume-dashboard')
                except:
                    # Profile doesn't exist - redirect to dashboard
                    return reverse('resumes:resume-dashboard')
                # User has resume - go to builder
                return reverse('resumes:resume-builder')
            elif user.user_type == 'employer':
                return reverse('jobs:my-jobs')
        
        # Fallback to default behavior
        return super().get_login_redirect_url(request)
    
    def get_signup_redirect_url(self, request):
        """
        Override the default signup redirect URL to redirect based on user type.
        For new job seekers, redirect to dashboard (upload/build options) instead of builder.
        """
        user = request.user
        
        # Check if user is authenticated and has a user_type
        if user.is_authenticated and hasattr(user, 'user_type'):
            if user.user_type == 'job_seeker':
                # For new users, redirect to dashboard to show upload/build options
                # Check if user has a resume - if not, go to dashboard
                try:
                    profile = user.jobseekerprofile
                    # Check if resume exists
                    from resumes.models import Resume
                    if not Resume.objects.filter(profile=profile).exists():
                        # New user without resume - show dashboard with options
                        return reverse('resumes:resume-dashboard')
                except:
                    # Profile doesn't exist yet - go to dashboard
                    return reverse('resumes:resume-dashboard')
                # User has a resume - go to builder
                return reverse('resumes:resume-builder')
            elif user.user_type == 'employer':
                return reverse('users:employer-onboarding')
        
        # Fallback to default behavior
        return super().get_signup_redirect_url(request)


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social account signups to handle user_type assignment
    and automatically connect social accounts to existing users.
    """
    
    def pre_social_login(self, request, sociallogin):
        """
        Called before a social account is logged in.
        Automatically connects social accounts to existing users with matching emails.
        """
        # If user is already authenticated, just connect the account
        if request.user.is_authenticated:
            return
        
        # If social account already exists, nothing to do (user will be logged in automatically)
        if sociallogin.is_existing:
            return
        
        # Get email from social account
        # Try multiple ways to get the email
        email = None
        if hasattr(sociallogin, 'account') and sociallogin.account.extra_data:
            email = sociallogin.account.extra_data.get('email') or sociallogin.account.extra_data.get('emailAddress')
        
        # Also try to get email from the social account's email field
        if not email and hasattr(sociallogin, 'email_addresses') and sociallogin.email_addresses:
            email = sociallogin.email_addresses[0].email
        
        # Fallback to user_email utility
        if not email:
            try:
                email = user_email(sociallogin.account)
            except:
                pass
        
        if not email:
            # No email available - allow normal signup flow
            return
        
        # Check if a user with this email already exists
        try:
            user = User.objects.get(email__iexact=email)  # Case-insensitive email match
            
            # Check if the social account is already connected to a different user
            from allauth.socialaccount.models import SocialAccount
            existing_social_account = SocialAccount.objects.filter(
                provider=sociallogin.account.provider,
                uid=sociallogin.account.uid
            ).first()
            
            if existing_social_account and existing_social_account.user != user:
                # Social account is already connected to a different user
                # Don't connect - let django-allauth handle this
                return
            
            # User exists and social account is not connected to another user
            # Connect the social account to the existing user
            # This will automatically log the user in
            try:
                sociallogin.connect(request, user)
                # Log the user in explicitly to ensure session is set
                from allauth.account.utils import perform_login
                perform_login(request, user, email_verification='none')
                # Add success message
                messages.success(request, f"Your {sociallogin.account.provider} account has been connected to your existing account!")
                # Redirect to appropriate page
                adapter = CustomAccountAdapter()
                redirect_url = adapter.get_login_redirect_url(request)
                raise ImmediateHttpResponse(HttpResponseRedirect(redirect_url))
            except Exception as e:
                # Connection failed - log error and allow normal signup flow
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Failed to connect social account: {str(e)}")
                # Allow normal signup flow to continue
                pass
        except User.DoesNotExist:
            # User doesn't exist - allow normal signup flow to continue
            pass
        except User.MultipleObjectsReturned:
            # Multiple users with same email (shouldn't happen, but handle it)
            # Get the first one and connect
            user = User.objects.filter(email__iexact=email).first()
            if user:
                try:
                    sociallogin.connect(request, user)
                    from allauth.account.utils import perform_login
                    perform_login(request, user, email_verification='none')
                    messages.success(request, f"Your {sociallogin.account.provider} account has been connected!")
                    adapter = CustomAccountAdapter()
                    redirect_url = adapter.get_login_redirect_url(request)
                    raise ImmediateHttpResponse(HttpResponseRedirect(redirect_url))
                except Exception as e:
                    # Connection failed - allow normal signup flow
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.error(f"Failed to connect social account: {str(e)}")
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
    
    def get_connect_redirect_url(self, request, socialaccount):
        """
        Redirect URL after connecting a social account.
        """
        # Redirect to edit profile page to show connected accounts
        return reverse('users:edit-profile')
    
    def is_auto_signup_allowed(self, request, sociallogin):
        """
        Allow automatic signup for social accounts.
        """
        return True
    
    def populate_user(self, request, sociallogin, data):
        """
        Populate user fields from social account data.
        """
        user = super().populate_user(request, sociallogin, data)
        # Ensure email is set
        email = user_email(sociallogin.account)
        if email and not user.email:
            user.email = email
        return user
