from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q

# Import necessary models for the caching logic
from jobs.models import JobPosting, JobMatchScore
from resumes.models import Resume
from users.models import JobSeekerProfile
# --- MODIFIED: Corrected imports to point to the source files ---
from resumes.parser import get_full_resume_text
from jobs.matcher import calculate_match_score
# --- END MODIFICATION ---

def home_view(request):
    # Check if the user is authenticated (logged in)
    if request.user.is_authenticated:
        # If they are an employer, show the employer dashboard
        if request.user.user_type == 'employer':
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
                resume_text = get_full_resume_text(applicant_resume)

                for job in jobs:
                    cached_score = JobMatchScore.objects.filter(resume=applicant_resume, job_posting=job).first()
                    
                    is_stale = (not cached_score or 
                                applicant_resume.updated_at > cached_score.last_calculated or 
                                job.updated_at > cached_score.last_calculated)

                    if is_stale:
                        job_text = f"{job.title} {job.description} {job.requirements}"
                        score = calculate_match_score(resume_text, job_text)
                        JobMatchScore.objects.update_or_create(
                            resume=applicant_resume, job_posting=job,
                            defaults={'score': score}
                        )
                    else:
                        score = cached_score.score
                    
                    jobs_with_scores.append({'job': job, 'score': score})
                # --- END CACHING LOGIC ---

                context = {'jobs_with_scores': jobs_with_scores}
                return render(request, 'pages/home_seeker.html', context)

            except (Resume.DoesNotExist, JobSeekerProfile.DoesNotExist):
                # If no resume, just show the jobs without scores
                context = {'jobs': jobs}
                return render(request, 'pages/home_seeker.html', context)
    
    # If the user is not logged in, show the public homepage
    return render(request, 'pages/home_public.html')

