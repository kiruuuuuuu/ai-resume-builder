from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, EmployerOnboardingForm, UserCredentialsForm, CustomPasswordChangeForm
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
    
    # Initialize forms with current user data
    credentials_form = UserCredentialsForm(instance=user)
    password_form = CustomPasswordChangeForm(user)
    
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
            password_form = CustomPasswordChangeForm(user, request.POST)
            if password_form.is_valid():
                password_form.save()
                # Update session to prevent logout after password change
                update_session_auth_hash(request, password_form.user)
                messages.success(request, "Your password has been changed successfully!")
                return redirect('users:edit-profile')
            # If form is invalid, password_form already has errors, credentials_form stays fresh
    
    # Determine which tab should be active based on form errors
    active_tab = 'credentials'
    if request.method == 'POST':
        if 'change_password' in request.POST and password_form.errors:
            active_tab = 'password'
        elif 'update_credentials' in request.POST and credentials_form.errors:
            active_tab = 'credentials'
    
    context = {
        'credentials_form': credentials_form,
        'password_form': password_form,
        'active_tab': active_tab,
    }
    
    return render(request, 'users/edit_profile.html', context)

