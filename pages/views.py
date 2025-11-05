from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q, Count

# Import necessary models for the caching logic
from jobs.models import JobPosting, JobMatchScore, Application
from resumes.models import Resume
from users.models import JobSeekerProfile, CustomUser
# Import async task for match score calculation
from jobs.tasks import calculate_and_save_match_score_task

def home_view(request):
    # Check if the user is authenticated (logged in)
    if request.user.is_authenticated:
        # If they are an employer, check onboarding status
        if request.user.user_type == 'employer':
            try:
                employer_profile = request.user.employerprofile
                # Redirect to onboarding if company details are missing
                if not (employer_profile.company_name and employer_profile.company_website and employer_profile.company_description):
                    from django.shortcuts import redirect
                    from django.urls import reverse
                    return redirect(reverse('users:employer-onboarding'))
            except AttributeError:
                from django.shortcuts import redirect
                from django.urls import reverse
                return redirect(reverse('users:employer-onboarding'))
            
            return render(request, 'pages/home_employer.html')
        # If they are a job seeker, show the job seeker dashboard with job listings
        else:
            jobs = JobPosting.objects.filter(
                Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
            ).order_by('-created_at')[:20]
            
            try:
                applicant_resume = Resume.objects.filter(profile=request.user.jobseekerprofile).latest('created_at')
                
                # --- START CACHING LOGIC ---
                jobs_with_scores = []
                job_ids = [job.id for job in jobs]
                
                # Fetch existing scores in one query for better performance
                existing_scores = JobMatchScore.objects.filter(
                    resume=applicant_resume, 
                    job_posting_id__in=job_ids
                ).values('job_posting_id', 'score', 'last_calculated')
                
                scores_map = {item['job_posting_id']: item for item in existing_scores}

                for job in jobs:
                    cached_score_data = scores_map.get(job.id)
                    
                    is_stale = (not cached_score_data or 
                                applicant_resume.updated_at > cached_score_data['last_calculated'] or 
                                job.updated_at > cached_score_data['last_calculated'])

                    if is_stale:
                        # Trigger background task instead of calculating synchronously
                        calculate_and_save_match_score_task.delay(applicant_resume.id, job.id)
                    
                    # Use cached score (may be stale, will update on next page refresh)
                    score = cached_score_data['score'] if cached_score_data else 0
                    jobs_with_scores.append({'job': job, 'score': score})
                # --- END CACHING LOGIC ---

                context = {'jobs_with_scores': jobs_with_scores}
                return render(request, 'pages/home_seeker.html', context)

            except (Resume.DoesNotExist, JobSeekerProfile.DoesNotExist):
                # If no resume, just show the jobs without scores
                context = {'jobs': jobs}
                return render(request, 'pages/home_seeker.html', context)
    
    # If the user is not logged in, show the public homepage
    # Get real statistics for the homepage
    total_users = CustomUser.objects.filter(is_active=True).count()
    total_resumes = Resume.objects.count()
    total_jobs = JobPosting.objects.filter(
        Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
    ).count()
    total_applications = Application.objects.count()
    
    context = {
        'total_users': total_users,
        'total_resumes': total_resumes,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
    }
    return render(request, 'pages/home_public.html', context)

