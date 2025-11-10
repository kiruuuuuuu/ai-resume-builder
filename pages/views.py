from django.shortcuts import render
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
import json
import base64
import re

# Import necessary models for the caching logic
from jobs.models import JobPosting, JobMatchScore, Application
from resumes.models import Resume
from users.models import JobSeekerProfile, CustomUser
# Import async task for match score calculation
from jobs.tasks import calculate_and_save_match_score_task
from .models import BugReport, Feedback

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
                applicant_resume = Resume.objects.filter(profile=request.user.jobseekerprofile).select_related('profile').latest('created_at')
                
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
                    # Use cached score only - match scoring is now triggered on resume/job updates
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

@require_POST
def report_bug_view(request):
    """
    API endpoint to receive bug reports from users.
    Accepts JSON with description, url, screenshot (base64), and browser_info.
    """
    try:
        data = json.loads(request.body)
        url = data.get('url', 'N/A')
        description = data.get('description', 'No description')
        screenshot_data = data.get('screenshot', None)  # Base64 encoded image
        browser_info = data.get('browser_info', None)
        
        # Sanitize user input
        from core.utils import sanitize_text
        description = sanitize_text(description)
        url = sanitize_text(url)
        if browser_info:
            browser_info = sanitize_text(browser_info)
        
        if not description or len(description.strip()) < 10:
            return JsonResponse({'status': 'error', 'message': 'Please provide a detailed description (at least 10 characters).'}, status=400)
        
        # Create bug report
        bug_report = BugReport.objects.create(
            user=request.user if request.user.is_authenticated else None,
            url=url[:1024],  # Ensure URL doesn't exceed max_length
            description=description,
            browser_info=browser_info[:255] if browser_info else None,
        )
        
        # Handle screenshot if provided (base64 encoded)
        if screenshot_data:
            try:
                # Remove data URL prefix if present (e.g., "data:image/png;base64,")
                if ',' in screenshot_data:
                    screenshot_data = screenshot_data.split(',')[1]
                
                # Decode base64 image
                image_data = base64.b64decode(screenshot_data)
                
                # Validate file size (max 10MB for screenshots)
                from django.conf import settings
                max_size = getattr(settings, 'MAX_SCREENSHOT_SIZE', 10 * 1024 * 1024)
                if len(image_data) > max_size:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f"Screenshot for bug report {bug_report.id} exceeds size limit")
                    # Continue without screenshot rather than failing the request
                else:
                    # Generate filename
                    import uuid
                    filename = f"bug_{bug_report.id}_{uuid.uuid4().hex[:8]}.png"
                    
                    # Save screenshot
                    bug_report.screenshot.save(filename, ContentFile(image_data), save=True)
            except Exception as e:
                # If screenshot processing fails, log but don't fail the entire request
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to process screenshot for bug report {bug_report.id}: {e}")
        
        return JsonResponse({'status': 'success', 'message': 'Bug report submitted successfully. Thank you!'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in report_bug_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while submitting the bug report.'}, status=500)


@require_POST
def submit_feedback_view(request):
    """
    API endpoint to receive feedback from users.
    Accepts JSON with feedback_type, message, and optional rating.
    """
    try:
        data = json.loads(request.body)
        feedback_type = data.get('feedback_type', 'general')
        message = data.get('message', '')
        rating = data.get('rating', None)
        
        # Validate feedback type
        valid_types = ['feature', 'improvement', 'general', 'other']
        if feedback_type not in valid_types:
            feedback_type = 'general'
        
        # Sanitize user input
        from core.utils import sanitize_text
        message = sanitize_text(message)
        
        if not message or len(message.strip()) < 10:
            return JsonResponse({'status': 'error', 'message': 'Please provide detailed feedback (at least 10 characters).'}, status=400)
        
        # Validate rating if provided
        if rating is not None:
            try:
                rating = int(rating)
                if rating < 1 or rating > 5:
                    rating = None
            except (ValueError, TypeError):
                rating = None
        
        # Create feedback
        feedback = Feedback.objects.create(
            user=request.user if request.user.is_authenticated else None,
            feedback_type=feedback_type,
            message=message,
            rating=rating,
        )
        
        return JsonResponse({'status': 'success', 'message': 'Thank you for your feedback! We appreciate your input.'})
        
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data.'}, status=400)
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in submit_feedback_view: {e}")
        return JsonResponse({'status': 'error', 'message': 'An error occurred while submitting feedback.'}, status=500)

