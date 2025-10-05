from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages # Import the messages framework
from .forms import CustomUserCreationForm, ProfileUpdateForm
from .models import JobSeekerProfile, EmployerProfile # Import EmployerProfile

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # --- THIS IS THE FIX ---
            # After creating the user, create the correct profile
            user_type = form.cleaned_data.get('user_type')
            if user_type == 'job_seeker':
                JobSeekerProfile.objects.create(user=user)
            elif user_type == 'employer':
                # For employers, we can use the username as a default company name
                EmployerProfile.objects.create(user=user, company_name=f"{user.username}'s Company")
            # --- END OF FIX ---

            login(request, user)
            messages.success(request, "Welcome! Your account has been created successfully.")
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            
            next_url = request.GET.get('next')
            if next_url:
                return redirect(next_url)
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
def edit_personal_details(request):
    try:
        profile = request.user.jobseekerprofile
    except JobSeekerProfile.DoesNotExist:
        profile = JobSeekerProfile.objects.create(user=request.user)

    if request.method == 'POST':
        # Pass the user instance to the form
        form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            # Since the user's email might have changed, update the user object in the session
            request.user.refresh_from_db()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('resumes:resume-dashboard')
    else:
        # Pass the user instance to the form
        form = ProfileUpdateForm(instance=profile, user=request.user)

    context = {
        'form': form,
        'title': 'Edit Personal Details'
    }
    return render(request, 'resumes/edit_item.html', context)

