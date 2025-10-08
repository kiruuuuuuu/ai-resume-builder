from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django import forms
from django.urls import reverse
from django.db.models import Q, Prefetch
from django.http import HttpResponse
from django.conf import settings
from django.template.loader import get_template

# Celery Task
from .tasks import calculate_and_save_match_score_task

try:
    from weasyprint import HTML, CSS
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
    ).order_by('-created_at')

    if request.user.is_authenticated and request.user.user_type == 'job_seeker':
        try:
            applicant_resume = Resume.objects.filter(profile=request.user.jobseekerprofile).latest('created_at')
            
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

            return render(request, 'jobs/job_list.html', {'jobs_with_scores': jobs_with_scores})

        except (Resume.DoesNotExist, JobSeekerProfile.DoesNotExist):
            pass # Fallback to showing jobs without scores

    return render(request, 'jobs/job_list.html', {'jobs': jobs})


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

    context = {'job': job, 'ranked_applicants': ranked_applicants}
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

    context = {'application': application, 'formset': formset}
    return render(request, 'jobs/schedule_interview.html', context)

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

    context = {'apps_with_interview': apps_with_data}
    return render(request, 'jobs/my_applications.html', context)

