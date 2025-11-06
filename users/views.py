from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomUserCreationForm, EmployerOnboardingForm
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
            messages.success(request, "Welcome! Your account has been created successfully.")
            
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
            messages.success(request, f"Welcome back, {user.username}!")
            
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
    
    # Check if already completed
    if employer_profile.company_name and employer_profile.company_website and employer_profile.company_description:
        return redirect('jobs:my-jobs')
    
    if request.method == 'POST':
        form = EmployerOnboardingForm(request.POST, instance=employer_profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Company profile completed! You can now post jobs.")
            return redirect('jobs:my-jobs')
    else:
        form = EmployerOnboardingForm(instance=employer_profile)
    
    return render(request, 'users/employer_onboarding.html', {'form': form})

