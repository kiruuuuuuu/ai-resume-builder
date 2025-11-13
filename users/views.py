from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.utils import timezone
from allauth.socialaccount.models import SocialAccount
from .forms import CustomUserCreationForm, EmployerOnboardingForm, UserCredentialsForm, CustomPasswordChangeForm, SetPasswordForm
from .models import JobSeekerProfile, EmployerProfile

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'job_seeker':
                JobSeekerProfile.objects.create(user=user)
            elif user_type == 'employer':
                EmployerProfile.objects.create(user=user)

            # Specify backend since we have multiple authentication backends configured
            backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user, backend=backend)
            
            # Get user's display name (full name if available, otherwise username)
            display_name = user.username
            if user_type == 'job_seeker':
                try:
                    profile = user.jobseekerprofile
                    if profile.full_name:
                        display_name = profile.full_name
                except JobSeekerProfile.DoesNotExist:
                    pass
            elif user_type == 'employer':
                try:
                    profile = user.employerprofile
                    if profile.company_name:
                        display_name = profile.company_name
                except EmployerProfile.DoesNotExist:
                    pass
            
            messages.success(request, f"Welcome, {display_name}! Your account has been created successfully.")
            
            # Redirect employers to onboarding
            if user_type == 'employer':
                return redirect('users:employer-onboarding')
            
            # Redirect job seekers to resume builder
            return redirect('resumes:resume-builder')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # AuthenticationForm.get_user() already handles backend, but we'll be explicit
            login(request, user, backend=user.backend if hasattr(user, 'backend') else 'django.contrib.auth.backends.ModelBackend')
            
            # Get user's display name (full name if available, otherwise username)
            display_name = user.username
            if user.user_type == 'job_seeker':
                try:
                    profile = user.jobseekerprofile
                    if profile.full_name:
                        display_name = profile.full_name
                except JobSeekerProfile.DoesNotExist:
                    pass
            elif user.user_type == 'employer':
                try:
                    profile = user.employerprofile
                    if profile.company_name:
                        display_name = profile.company_name
                except EmployerProfile.DoesNotExist:
                    pass
            
            messages.success(request, f"Welcome back, {display_name}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
            else:
                # Redirect based on user type
                if user.user_type == 'job_seeker':
                    return redirect('resumes:resume-builder')
                elif user.user_type == 'employer':
                    return redirect('jobs:my-jobs')
                else:
                    return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

@login_required
def employer_onboarding_view(request):
    """Mandatory onboarding page for employers to fill company details."""
    if request.user.user_type != 'employer':
        messages.error(request, "This page is for employers only.")
        return redirect('home')
    
    try:
        employer_profile = request.user.employerprofile
    except EmployerProfile.DoesNotExist:
        employer_profile = EmployerProfile.objects.create(user=request.user)
    
    # Check if already completed (only redirect if not editing)
    is_editing = request.GET.get('edit', False) or request.path == '/users/edit-profile/'
    if employer_profile.company_name and employer_profile.company_website and employer_profile.company_description and not is_editing:
        return redirect('jobs:my-jobs')
    
    if request.method == 'POST':
        form = EmployerOnboardingForm(request.POST, instance=employer_profile)
        if form.is_valid():
            form.save()
            if is_editing:
                messages.success(request, "Profile updated successfully!")
            else:
                messages.success(request, "Company profile completed! You can now post jobs.")
            return redirect('jobs:my-jobs')
    else:
        form = EmployerOnboardingForm(instance=employer_profile)
    
    return render(request, 'users/employer_onboarding.html', {'form': form, 'is_editing': is_editing})

@login_required
def edit_profile_view(request):
    """Dedicated edit profile page for managing login credentials and password."""
    user = request.user
    
    # Check if user has a usable password (not a social account user)
    has_password = user.has_usable_password()
    
    # Get social accounts linked to this user
    social_accounts = SocialAccount.objects.filter(user=user)
    
    # Initialize forms with current user data
    credentials_form = UserCredentialsForm(instance=user)
    
    # Use SetPasswordForm if user doesn't have a password, otherwise use CustomPasswordChangeForm
    if has_password:
        password_form = CustomPasswordChangeForm(user)
    else:
        password_form = SetPasswordForm(user)
    
    # Handle credentials update
    if request.method == 'POST':
        if 'update_credentials' in request.POST:
            credentials_form = UserCredentialsForm(request.POST, instance=user)
            if credentials_form.is_valid():
                credentials_form.save()
                messages.success(request, "Your login credentials have been updated successfully!")
                return redirect('users:edit-profile')
            # If form is invalid, credentials_form already has errors, password_form stays fresh
        
        elif 'change_password' in request.POST:
            if has_password:
                password_form = CustomPasswordChangeForm(user, request.POST)
            else:
                password_form = SetPasswordForm(user, request.POST)
            
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout after password change
                update_session_auth_hash(request, password_form.user)
                if has_password:
                    messages.success(request, "Your password has been changed successfully!")
                else:
                    messages.success(request, "Password has been set successfully! You can now login with your email and password.")
                return redirect('users:edit-profile')
            # If form is invalid, password_form already has errors, credentials_form stays fresh
        
        elif 'disconnect_account' in request.POST:
            # Handle disconnecting a social account
            provider_id = request.POST.get('provider_id')
            try:
                social_account = SocialAccount.objects.get(user=user, provider=provider_id)
                # Only allow disconnecting if user has a password or other social accounts
                if user.has_usable_password() or social_accounts.count() > 1:
                    social_account.delete()
                    messages.success(request, f"Your {provider_id} account has been disconnected successfully.")
                else:
                    messages.error(request, "You cannot disconnect your last login method. Please set a password first.")
            except SocialAccount.DoesNotExist:
                messages.error(request, "Social account not found.")
            return redirect('users:edit-profile')
    
    # Determine which tab should be active based on form errors
    active_tab = 'credentials'
    if request.method == 'POST':
        if 'change_password' in request.POST and password_form.errors:
            active_tab = 'password'
        elif 'update_credentials' in request.POST and credentials_form.errors:
            active_tab = 'credentials'
        elif request.POST.get('active_tab'):
            active_tab = request.POST.get('active_tab')
    
    context = {
        'credentials_form': credentials_form,
        'password_form': password_form,
        'active_tab': active_tab,
        'has_password': has_password,
        'social_accounts': social_accounts,
    }
    
    return render(request, 'users/edit_profile.html', context)


def admin_login_view(request):
    """Custom admin login page - only accessible to staff/superusers."""
    if request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser):
        return redirect('users:admin-dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            # Check if user is staff or superuser
            if not (user.is_staff or user.is_superuser):
                messages.error(request, "Access denied. This page is for administrators only.")
                return redirect('users:admin-login')
            
            login(request, user, backend=user.backend if hasattr(user, 'backend') else 'django.contrib.auth.backends.ModelBackend')
            messages.success(request, f"Welcome, {user.username}!")
            return redirect('users:admin-dashboard')
    else:
        form = AuthenticationForm()
    
    return render(request, 'users/admin_login.html', {'form': form})


@staff_member_required
def admin_dashboard_view(request):
    """Main admin dashboard with bug reports, user stats, and system health."""
    from pages.models import BugReport
    from resumes.models import Resume
    from django.utils import timezone
    from datetime import timedelta
    
    # Bug Reports Statistics
    total_bugs = BugReport.objects.count()
    unresolved_bugs = BugReport.objects.filter(is_resolved=False).count()
    recent_bugs = BugReport.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    bug_reports = BugReport.objects.all().order_by('-created_at')[:10]
    
    # User Statistics
    from django.contrib.auth import get_user_model
    User = get_user_model()
    total_users = User.objects.count()
    active_users = User.objects.filter(last_login__gte=timezone.now() - timedelta(days=30)).count()
    job_seekers = User.objects.filter(user_type='job_seeker').count()
    employers = User.objects.filter(user_type='employer').count()
    
    # Resume Statistics
    total_resumes = Resume.objects.count()
    recent_resumes = Resume.objects.filter(created_at__gte=timezone.now() - timedelta(days=7)).count()
    
    # System Health (basic checks)
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        db_status = "Connected"
    except Exception as e:
        db_status = f"Error: {str(e)}"
    
    context = {
        'total_bugs': total_bugs,
        'unresolved_bugs': unresolved_bugs,
        'recent_bugs': recent_bugs,
        'bug_reports': bug_reports,
        'total_users': total_users,
        'active_users': active_users,
        'job_seekers': job_seekers,
        'employers': employers,
        'total_resumes': total_resumes,
        'recent_resumes': recent_resumes,
        'db_status': db_status,
    }
    
    return render(request, 'users/admin_dashboard.html', context)


@staff_member_required
def admin_bug_detail_view(request, bug_id):
    """View detailed bug report."""
    from pages.models import BugReport
    bug = get_object_or_404(BugReport, id=bug_id)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'resolve':
            bug.is_resolved = True
            bug.resolved_at = timezone.now()
            bug.resolved_by = request.user
            bug.resolution_notes = request.POST.get('resolution_notes', '')
            bug.save()
            messages.success(request, f"Bug #{bug.id} marked as resolved.")
            return redirect('users:admin-dashboard')
    
    return render(request, 'users/admin_bug_detail.html', {'bug': bug})

