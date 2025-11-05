from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.urls import reverse
from django.db.models import Q, Prefetch
from django.http import HttpResponse, JsonResponse
from icalendar import Calendar, Event
from datetime import timedelta
from django.conf import settings
from django.template.loader import get_template
import json
import logging

logger = logging.getLogger(__name__)

# Celery Task
from .tasks import calculate_and_save_match_score_task

WEASY_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    WEASY_AVAILABLE = True
except (ImportError, OSError):
    HTML = None
    CSS = None


# Models
from .models import JobPosting, Application, Notification, Interview, InterviewSlot, JobMatchScore
from users.models import EmployerProfile, JobSeekerProfile
from resumes.models import Resume, Experience, Education, Skill, Project, Certification, Achievement, Language, Hobby
from resumes.parser import get_full_resume_text
# --- THE FIX IS HERE ---
from resumes.templatetags.resume_extras import get_resume_completeness_errors


# Forms
from .forms import JobPostingForm, InterviewSlotForm


@login_required
def post_job_view(request):
    if request.user.user_type != 'employer':
        messages.error(request, "This page is for employers only.")
        return redirect('home')

    try:
        employer_profile = request.user.employerprofile
    except EmployerProfile.DoesNotExist:
        employer_profile = EmployerProfile.objects.create(user=request.user, company_name=f"{request.user.username}'s Company")

    if request.method == 'POST':
        form = JobPostingForm(request.POST)
        if form.is_valid():
            job_posting = form.save(commit=False)
            job_posting.employer = employer_profile
            job_posting.save()
            messages.success(request, "Your job has been posted successfully!")
            return redirect('jobs:my-jobs')
    else:
        form = JobPostingForm()
    return render(request, 'jobs/post_job.html', {'form': form, 'is_editing': False})

@login_required
def generate_job_description_api(request):
    """AJAX endpoint to generate job description using AI."""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            job_title = data.get('title', '').strip()
            keywords = data.get('keywords', '').strip()
            
            if not job_title:
                return JsonResponse({'error': 'Job title is required.'}, status=400)
            
            from .matcher import generate_job_description
            result = generate_job_description(job_title, keywords)
            
            if result.get('description') and result.get('requirements'):
                return JsonResponse({
                    'status': 'success',
                    'description': result['description'],
                    'requirements': result['requirements']
                })
            else:
                return JsonResponse({'error': 'Failed to generate job description.'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            logger.error(f"Error in generate_job_description_api: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def generate_applicant_summary_api(request):
    """AJAX endpoint to generate AI summary for an applicant."""
    if request.user.user_type != 'employer':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            application_id = data.get('application_id')
            
            if not application_id:
                return JsonResponse({'error': 'Application ID is required.'}, status=400)
            
            application = get_object_or_404(Application, id=application_id)
            
            # Verify employer owns the job
            if application.job_posting.employer.user != request.user:
                return JsonResponse({'error': 'Unauthorized'}, status=403)
            
            # Get applicant's latest resume
            try:
                applicant_resume = Resume.objects.filter(profile=application.applicant).latest('created_at')
            except Resume.DoesNotExist:
                return JsonResponse({'error': 'Applicant has no resume.'}, status=404)
            
            # Get resume text and job description
            from resumes.parser import get_full_resume_text
            resume_text = get_full_resume_text(applicant_resume)
            job_description = f"{application.job_posting.title}\n\n{application.job_posting.description}\n\n{application.job_posting.requirements}"
            
            if not resume_text.strip():
                return JsonResponse({'error': 'Resume is empty.'}, status=400)
            
            from .matcher import generate_applicant_summary
            summary = generate_applicant_summary(resume_text, job_description)
            
            if summary:
                return JsonResponse({
                    'status': 'success',
                    'summary': summary
                })
            else:
                return JsonResponse({'error': 'Failed to generate summary.'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            logger.error(f"Error in generate_applicant_summary_api: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def generate_interview_prep_api(request):
    """AJAX endpoint to generate AI interview preparation questions."""
    if request.user.user_type != 'job_seeker':
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            application_id = data.get('application_id')
            
            if not application_id:
                return JsonResponse({'error': 'Application ID is required.'}, status=400)
            
            application = get_object_or_404(Application, id=application_id, applicant__user=request.user)
            
            # Get applicant's latest resume
            try:
                applicant_resume = Resume.objects.filter(profile=application.applicant).latest('created_at')
            except Resume.DoesNotExist:
                return JsonResponse({'error': 'You have no resume. Please create one first.'}, status=404)
            
            # Get resume text and job description
            from resumes.parser import get_full_resume_text
            resume_text = get_full_resume_text(applicant_resume)
            job_description = f"{application.job_posting.title}\n\n{application.job_posting.description}\n\n{application.job_posting.requirements}"
            
            if not resume_text.strip():
                return JsonResponse({'error': 'Resume is empty.'}, status=400)
            
            from .matcher import generate_interview_prep
            result = generate_interview_prep(resume_text, job_description)
            
            if result.get('questions') and len(result['questions']) > 0:
                return JsonResponse({
                    'status': 'success',
                    'questions': result['questions']
                })
            else:
                return JsonResponse({'error': 'Failed to generate interview prep questions.'}, status=500)
                
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data.'}, status=400)
        except Exception as e:
            logger.error(f"Error in generate_interview_prep_api: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def interview_prep_view(request, application_id):
    """Dedicated page to display AI-generated interview preparation questions."""
    if request.user.user_type != 'job_seeker':
        messages.error(request, "This page is for job seekers only.")
        return redirect('home')
    
    application = get_object_or_404(Application, id=application_id, applicant__user=request.user)
    
    # Get applicant's latest resume
    try:
        applicant_resume = Resume.objects.filter(profile=application.applicant).latest('created_at')
    except Resume.DoesNotExist:
        messages.error(request, "You have no resume. Please create one first.")
        return redirect('resumes:resume-dashboard')
    
    # Get resume text and job description
    resume_text = get_full_resume_text(applicant_resume)
    job_description = f"{application.job_posting.title}\n\n{application.job_posting.description}\n\n{application.job_posting.requirements}"
    
    if not resume_text.strip():
        messages.error(request, "Resume is empty.")
        return redirect('resumes:resume-dashboard')
    
    # Generate interview prep questions
    # This may take a few seconds, so we show a loading state via button disable
    try:
        from .matcher import generate_interview_prep
        result = generate_interview_prep(resume_text, job_description)
        questions = result.get('questions', []) if result else []
        
        # Ensure questions are properly formatted (list of dicts)
        if questions:
            # Convert to list of dicts if needed
            formatted_questions = []
            for q in questions:
                if isinstance(q, dict):
                    # Ensure both question and answer keys exist - try multiple key variations
                    question_text = (q.get('question') or q.get('Question') or 
                                   q.get('q') or q.get('Q') or '')
                    answer_text = (q.get('answer') or q.get('Answer') or 
                                 q.get('a') or q.get('A') or '')
                    formatted_questions.append({
                        'question': str(question_text) if question_text else '',
                        'answer': str(answer_text) if answer_text else ''
                    })
                else:
                    # Handle case where it might be a different structure
                    formatted_questions.append({
                        'question': str(q) if q else '',
                        'answer': ''
                    })
            questions = formatted_questions
            logger.info(f"Formatted {len(questions)} questions for interview prep")
            # Debug: Log first question structure
            if questions:
                logger.info(f"First question structure: {questions[0]}")
                logger.info(f"First question keys: {questions[0].keys() if isinstance(questions[0], dict) else 'Not a dict'}")
    except Exception as e:
        logger.error(f"Error generating interview prep: {e}")
        questions = []
        messages.warning(request, "There was an issue generating interview questions. Please try again.")
    
    context = {
        'application': application,
        'job_posting': application.job_posting,
        'questions': questions,
        'resume': applicant_resume,
    }
    
    return render(request, 'jobs/interview_prep.html', context)

def company_profile_view(request, employer_id):
    """Public company profile page."""
    employer_profile = get_object_or_404(EmployerProfile, user_id=employer_id)
    
    # Get active jobs
    active_jobs = JobPosting.objects.filter(
        employer=employer_profile
    ).filter(
        Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
    ).order_by('-created_at')[:10]
    
    context = {
        'company': employer_profile,
        'active_jobs': active_jobs,
    }
    
    return render(request, 'jobs/company_profile.html', context)

@login_required
def edit_job_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    if request.method == 'POST':
        form = JobPostingForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, "Job posting updated successfully.")
            return redirect('jobs:my-jobs')
    else:
        form = JobPostingForm(instance=job)
    context = {'form': form, 'is_editing': True}
    return render(request, 'jobs/post_job.html', context)

def job_list_view(request):
    jobs = JobPosting.objects.filter(
        Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
    )
    
    # Search and filter logic
    search_query = request.GET.get('search', '').strip()
    location_query = request.GET.get('location', '').strip()
    salary_min = request.GET.get('salary_min')
    salary_max = request.GET.get('salary_max')
    sort_by = request.GET.get('sort', 'newest')
    
    # Apply search filter
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(requirements__icontains=search_query) |
            Q(employer__company_name__icontains=search_query)
        )
    
    # Apply location filter
    if location_query:
        jobs = jobs.filter(location__icontains=location_query)
    
    # Apply salary filters (check both new and old fields for compatibility)
    if salary_min:
        try:
            min_val = int(salary_min)
            jobs = jobs.filter(
                Q(salary_min__gte=min_val) | Q(salary_max__gte=min_val) |
                Q(salary_range__icontains=str(min_val))  # Fallback for old salary_range field
            )
        except ValueError:
            pass
    
    if salary_max:
        try:
            max_val = int(salary_max)
            jobs = jobs.filter(
                Q(salary_max__lte=max_val) | Q(salary_min__lte=max_val) |
                Q(salary_range__icontains=str(max_val))  # Fallback for old salary_range field
            )
        except ValueError:
            pass
    
    # Apply sorting
    if sort_by == 'oldest':
        jobs = jobs.order_by('created_at')
    elif sort_by == 'title':
        jobs = jobs.order_by('title')
    elif sort_by == 'company':
        jobs = jobs.order_by('employer__company_name')
    else:  # newest (default)
        jobs = jobs.order_by('-created_at')

    has_resume = False
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        try:
            applicant_resume = Resume.objects.filter(profile=request.user.jobseekerprofile).latest('created_at')
            has_resume = True
            
            jobs_with_scores = []
            job_ids = [job.id for job in jobs]
            
            # Fetch existing scores in one query
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
                    # Trigger background task instead of calculating here
                    calculate_and_save_match_score_task.delay(applicant_resume.id, job.id)
                
                score = cached_score_data['score'] if cached_score_data else 0
                jobs_with_scores.append({'job': job, 'score': score})

            return render(request, 'jobs/job_list.html', {
                'jobs_with_scores': jobs_with_scores,
                'has_resume': has_resume
            })

        except (Resume.DoesNotExist, JobSeekerProfile.DoesNotExist):
            pass # Fallback to showing jobs without scores

    return render(request, 'jobs/job_list.html', {
        'jobs': jobs,
        'has_resume': has_resume
    })


def job_detail_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    has_applied = False
    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        has_applied = Application.objects.filter(job_posting=job, applicant=request.user.jobseekerprofile).exists()
    
    context = {
        'job': job,
        'has_applied': has_applied,
        'is_active': job.is_active
    }
    return render(request, 'jobs/job_detail.html', context)

@login_required
def apply_for_job_view(request, job_id):
    job = get_object_or_404(JobPosting, id=job_id)
    
    if not job.is_active:
        messages.error(request, "The application deadline for this job has passed.")
        return redirect('jobs:job-detail', job_id=job.id)

    if request.user.user_type != 'job_seeker':
        messages.error(request, "Only Job Seekers can apply for jobs.")
        return redirect('home')
        
    # --- THE FIX IS HERE ---
    # This logic now checks for a minimum viable resume and provides a detailed error message.
    try:
        applicant_resume = Resume.objects.filter(profile=request.user.jobseekerprofile).latest('created_at')
        missing_items = get_resume_completeness_errors(applicant_resume)
        if missing_items:
            # Construct a user-friendly error message and raise an exception to be caught below.
            error_message = "Your resume is incomplete. Please add " + ", and ".join(missing_items) + " before applying."
            raise ValueError(error_message)

    except (Resume.DoesNotExist, JobSeekerProfile.DoesNotExist):
        messages.error(request, "You must create a resume before applying.")
        return redirect('resumes:resume-dashboard')
    except ValueError as e:
        # Catch the custom error message and display it to the user.
        messages.error(request, str(e))
        return redirect('resumes:resume-builder')


    applicant_profile = request.user.jobseekerprofile

    if Application.objects.filter(job_posting=job, applicant=applicant_profile).exists():
        messages.warning(request, "You have already applied for this job.")
        return redirect('jobs:job-detail', job_id=job.id)

    if request.method == 'POST':
        template_choice = request.POST.get('template_choice', 'classic')
        Application.objects.create(
            job_posting=job, 
            applicant=applicant_profile,
            resume_template=template_choice
        )
        
        notification_link = reverse('jobs:view-applicants', args=[job.id])
        Notification.objects.create(
            recipient=job.employer.user,
            message=f"New application for '{job.title}' from {applicant_profile.full_name or applicant_profile.user.username}.",
            link=notification_link
        )

        messages.success(request, f"You have successfully applied for the position of {job.title}.")
        return redirect('jobs:job-detail', job_id=job.id)

    return redirect('jobs:job-detail', job_id=job.id)


@login_required
def employer_jobs_view(request):
    if request.user.user_type != 'employer':
        messages.error(request, "This page is for employers only.")
        return redirect('home')
    try:
        employer_profile = request.user.employerprofile
    except EmployerProfile.DoesNotExist:
        employer_profile = EmployerProfile.objects.create(user=request.user, company_name=f"{request.user.username}'s Company")
    jobs = JobPosting.objects.filter(employer=employer_profile).order_by('-created_at')
    return render(request, 'jobs/employer_jobs.html', {'jobs': jobs})

@login_required
def view_applicants_view(request, job_id):
    if request.user.user_type != 'employer':
        messages.error(request, "This page is for employers only.")
        return redirect('home')

    job = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    
    applications = Application.objects.filter(job_posting=job).select_related(
        'applicant__user'
    ).prefetch_related(
        Prefetch('interview', queryset=Interview.objects.all())
    )
    
    ranked_applicants = []
    for app in applications:
        try:
            applicant_resume = Resume.objects.filter(profile=app.applicant).latest('created_at')
            
            cached_score_data = JobMatchScore.objects.filter(resume=applicant_resume, job_posting=job).first()
            
            is_stale = (not cached_score_data or 
                        applicant_resume.updated_at > cached_score_data.last_calculated or 
                        job.updated_at > cached_score_data.last_calculated)

            if is_stale:
                calculate_and_save_match_score_task.delay(applicant_resume.id, job.id)

            score = cached_score_data.score if cached_score_data else 0
            interview = getattr(app, 'interview', None)
            
            ranked_applicants.append({'application': app, 'score': score, 'interview': interview})
        except Resume.DoesNotExist:
            ranked_applicants.append({'application': app, 'score': 0, 'interview': None})

    ranked_applicants.sort(key=lambda x: x['score'], reverse=True)

    # Calculate score distribution for chart
    score_ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '50-59': 0,
        '0-49': 0
    }
    
    for item in ranked_applicants:
        score = item['score']
        if score >= 90:
            score_ranges['90-100'] += 1
        elif score >= 80:
            score_ranges['80-89'] += 1
        elif score >= 70:
            score_ranges['70-79'] += 1
        elif score >= 60:
            score_ranges['60-69'] += 1
        elif score >= 50:
            score_ranges['50-59'] += 1
        else:
            score_ranges['0-49'] += 1

    context = {'job': job, 'ranked_applicants': ranked_applicants, 'score_distribution': score_ranges}
    return render(request, 'jobs/view_applicants.html', context)


@login_required
def view_applicant_resume(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    if request.user != application.job_posting.employer.user:
        messages.error(request, "You are not authorized to view this resume.")
        return redirect('home')
    
    try:
        resume = Resume.objects.filter(profile=application.applicant).latest('created_at')
    except Resume.DoesNotExist:
        messages.error(request, "The applicant does not have a resume to display.")
        return redirect('jobs:view-applicants', job_id=application.job_posting.id)

    template_name = application.resume_template
    
    skills_by_category = {}
    skills_qs = Skill.objects.filter(resume=resume).order_by('category')
    for skill in skills_qs:
        category = skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill.name)

    context = {
        'resume': resume,
        'experiences': Experience.objects.filter(resume=resume).order_by('-start_date'),
        'educations': Education.objects.filter(resume=resume).order_by('-start_date'),
        'skills_by_category': skills_by_category,
        'projects': Project.objects.filter(resume=resume),
        'certifications': Certification.objects.filter(resume=resume),
        'achievements': Achievement.objects.filter(resume=resume),
        'languages': Language.objects.filter(resume=resume),
        'hobbies': [hobby.name for hobby in Hobby.objects.filter(resume=resume)],
        'settings': settings,
    }
    
    template_path = f'resumes/resume_pdf_{template_name}.html'
    template = get_template(template_path)
    html = template.render(context)

    if not WEASY_AVAILABLE:
        return HttpResponse('PDF generation failed: WeasyPrint is not installed or configured correctly.')

    try:
        html_obj = HTML(string=html, base_url=request.build_absolute_uri('/'))
        pdf_bytes = html_obj.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1.5cm }')])
    except Exception as e:
        return HttpResponse('PDF generation (WeasyPrint) failed: ' + str(e) + '<pre>' + html + '</pre>')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{resume.profile.full_name}_resume.pdf"'
    return response


@login_required
def update_application_status(request, application_id):
    application = get_object_or_404(Application, id=application_id, job_posting__employer=request.user.employerprofile)
    action = request.GET.get('action')

    valid_actions = {
        'review': 'Under Review',
        'shortlist': 'Shortlisted',
        'reject': 'Rejected',
        'offer': 'Offered'
    }

    if action in valid_actions:
        new_status = valid_actions[action]
        application.status = new_status
        application.save()
        Notification.objects.create(
            recipient=application.applicant.user,
            message=f"Update on your application for '{application.job_posting.title}': Status changed to {new_status}.",
            link=reverse('jobs:my-applications')
        )
        messages.success(request, f"Application status updated to {new_status}.")
    else:
        messages.error(request, "Invalid action.")
        
    return redirect('jobs:view-applicants', job_id=application.job_posting.id)

@login_required
def schedule_interview_view(request, application_id):
    application = get_object_or_404(Application, id=application_id, job_posting__employer=request.user.employerprofile)
    InterviewSlotFormSet = forms.formset_factory(InterviewSlotForm, extra=3, min_num=1, validate_min=True)
    
    interview, created = Interview.objects.get_or_create(application=application)

    if request.method == 'POST':
        formset = InterviewSlotFormSet(request.POST)
        if formset.is_valid():
            interview.slots.all().delete()
            
            interview_details = formset.cleaned_data[0].get('interview_details')
            interview.interview_details = interview_details
            interview.status = 'Proposed'
            application.status = 'Interview'
            application.save()
            interview.save()
            
            for form in formset:
                proposed_time = form.cleaned_data.get('proposed_time')
                if proposed_time:
                    InterviewSlot.objects.create(interview=interview, proposed_time=proposed_time)
            
            notification_link = reverse('jobs:respond-to-interview', args=[interview.id])
            Notification.objects.create(
                recipient=application.applicant.user,
                message=f"You have an interview proposal for '{application.job_posting.title}'.",
                link=notification_link
            )
            messages.success(request, f"Interview slots proposed to {application.applicant.full_name}.")
            return redirect('jobs:view-applicants', job_id=application.job_posting.id)
    else:
        formset = InterviewSlotFormSet()

    context = {'application': application, 'formset': formset, 'interview': interview}
    return render(request, 'jobs/schedule_interview.html', context)

@login_required
def download_interview_calendar(request, interview_id):
    """Generate and download .ics calendar file for interview."""
    interview = get_object_or_404(Interview, id=interview_id)
    
    # Verify user has permission (employer or applicant)
    if request.user != interview.application.job_posting.employer.user and request.user != interview.application.applicant.user:
        messages.error(request, "You are not authorized to access this calendar.")
        return redirect('home')
    
    # Determine which time to use
    interview_time = interview.confirmed_slot
    if not interview_time and interview.slots.exists():
        interview_time = interview.slots.first().proposed_time
    
    if not interview_time:
        messages.error(request, "No interview time available.")
        redirect_url = 'jobs:my-applications' if request.user.user_type == 'job_seeker' else reverse('jobs:view-applicants', args=[interview.application.job_posting.id])
        return redirect(redirect_url)
    
    # Create calendar
    cal = Calendar()
    cal.add('prodid', '-//AI Resume Builder//Interview Calendar//EN')
    cal.add('version', '2.0')
    
    # Create event
    event = Event()
    event.add('summary', f"Interview: {interview.application.job_posting.title}")
    event.add('description', f"Interview for {interview.application.job_posting.title} at {interview.application.job_posting.employer.company_name}\n\n{interview.interview_details or ''}")
    event.add('dtstart', interview_time)
    event.add('dtend', interview_time + timedelta(hours=1))
    event.add('dtstamp', timezone.now())
    event.add('location', interview.interview_details or 'TBD')
    event.add('organizer', interview.application.job_posting.employer.user.email)
    event.add('attendee', interview.application.applicant.user.email)
    event.add('status', 'CONFIRMED')
    
    cal.add_component(event)
    
    # Generate response
    response = HttpResponse(cal.to_ical(), content_type='text/calendar')
    response['Content-Disposition'] = f'attachment; filename="interview_{interview.id}.ics"'
    return response

@login_required
def job_stats_view(request, job_id):
    """Job statistics dashboard with charts."""
    if request.user.user_type != 'employer':
        messages.error(request, "This page is for employers only.")
        return redirect('home')
    
    job = get_object_or_404(JobPosting, id=job_id, employer=request.user.employerprofile)
    applications = Application.objects.filter(job_posting=job)
    
    # Applications over time (last 30 days)
    from django.db.models import Count
    from django.db.models.functions import TruncDate
    thirty_days_ago = timezone.now() - timedelta(days=30)
    applications_over_time = applications.filter(applied_at__gte=thirty_days_ago).annotate(
        date=TruncDate('applied_at')
    ).values('date').annotate(count=Count('id')).order_by('date')
    
    # Create date list for chart
    date_counts = {}
    for item in applications_over_time:
        date_counts[item['date'].isoformat()] = item['count']
    
    # Score distribution
    score_ranges = {
        '90-100': 0,
        '80-89': 0,
        '70-79': 0,
        '60-69': 0,
        '50-59': 0,
        '0-49': 0
    }
    
    for app in applications:
        try:
            resume = Resume.objects.filter(profile=app.applicant).latest('created_at')
            score_data = JobMatchScore.objects.filter(resume=resume, job_posting=job).first()
            if score_data:
                score = score_data.score
                if score >= 90:
                    score_ranges['90-100'] += 1
                elif score >= 80:
                    score_ranges['80-89'] += 1
                elif score >= 70:
                    score_ranges['70-79'] += 1
                elif score >= 60:
                    score_ranges['60-69'] += 1
                elif score >= 50:
                    score_ranges['50-59'] += 1
                else:
                    score_ranges['0-49'] += 1
        except Resume.DoesNotExist:
            pass
    
    # Status distribution
    status_counts = applications.values('status').annotate(count=Count('status'))
    status_data = {item['status']: item['count'] for item in status_counts}
    
    # Serialize data for JavaScript
    context = {
        'job': job,
        'applications_count': applications.count(),
        'date_counts': json.dumps(date_counts),
        'score_distribution': json.dumps(score_ranges),
        'status_data': json.dumps(status_data),
    }
    
    return render(request, 'jobs/job_stats.html', context)

@login_required
def respond_to_interview_view(request, interview_id):
    interview = get_object_or_404(Interview, id=interview_id, application__applicant=request.user.jobseekerprofile)
    
    if request.method == 'POST':
        slot_id = request.POST.get('slot')
        if slot_id:
            selected_slot = get_object_or_404(InterviewSlot, id=slot_id, interview=interview)
            
            interview.confirmed_slot = selected_slot.proposed_time
            interview.status = 'Scheduled'
            interview.save()
            
            interview.slots.exclude(id=slot_id).delete()
            
            notification_link = reverse('jobs:view-applicants', args=[interview.application.job_posting.id])
            Notification.objects.create(
                recipient=interview.application.job_posting.employer.user,
                message=f"{interview.application.applicant.full_name} has confirmed their interview for '{interview.application.job_posting.title}'.",
                link=notification_link
            )

            messages.success(request, "Interview time confirmed successfully!")
            return redirect('jobs:my-applications')

    context = {'interview': interview}
    return render(request, 'jobs/respond_to_interview.html', context)


@login_required
def mark_notification_as_read_view(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, recipient=request.user)
    if not notification.is_read:
        notification.is_read = True
        notification.save()
    return redirect(notification.link)

@login_required
def my_applications_view(request):
    if request.user.user_type != 'job_seeker':
        messages.error(request, "This page is for job seekers only.")
        return redirect('home')

    try:
        profile = request.user.jobseekerprofile
        applications = Application.objects.filter(applicant=profile).order_by('-applied_at')
        
        steps = ['Submitted', 'Under Review', 'Shortlisted', 'Interview', 'Offered']
        
        # Calculate status distribution for chart
        from django.db.models import Count
        status_counts = applications.values('status').annotate(count=Count('status'))
        status_data = {item['status']: item['count'] for item in status_counts}
        
        apps_with_data = []
        for app in applications:
            interview = Interview.objects.filter(application=app).first()
            
            current_index = -1
            current_status = app.status
            if current_status == 'Approved':
                current_status = 'Shortlisted'

            try:
                current_index = steps.index(current_status)
            except ValueError:
                current_index = -1

            apps_with_data.append({
                'application': app, 
                'interview': interview,
                'steps': steps,
                'current_index': current_index
            })

    except JobSeekerProfile.DoesNotExist:
        apps_with_data = []
        status_data = {}

    context = {'apps_with_interview': apps_with_data, 'status_data': status_data}
    return render(request, 'jobs/my_applications.html', context)

