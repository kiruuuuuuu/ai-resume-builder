from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.forms import formset_factory
from django.template.loader import get_template
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.core.exceptions import MultipleObjectsReturned
import datetime
import json

# Celery Tasks
from .tasks import parse_resume_task, update_resume_score_task

WEASY_AVAILABLE = False
try:
    from weasyprint import HTML, CSS
    WEASY_AVAILABLE = True
except (ImportError, OSError):
    HTML = None
    CSS = None

# Models
from users.models import JobSeekerProfile
from .models import (
    Resume, Experience, Education, Skill, Project, Certification, 
    Achievement, Language, Hobby, ParsedResumeCache
)

# Forms
from .forms import (
    ExperienceForm, EducationForm, SkillForm, UploadResumeForm,
    ProjectForm, CertificationForm, AchievementForm, LanguageForm, HobbyForm
)
from users.forms import ProfileUpdateForm

# AI Parser
from .parser import (
    extract_text_from_docx, extract_text_from_pdf,
    enhance_text_with_gemini
)

# --- Helper Function ---
def clean_date(date_str):
    if not date_str or not isinstance(date_str, str):
        return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%b %d, %Y', '%B %d, %Y'):
        try:
            return datetime.datetime.strptime(date_str, fmt).strftime('%Y-%m-%d')
        except (ValueError, TypeError):
            continue
    return None

# --- Main Views ---
@login_required
def resume_dashboard_view(request):
    try:
        profile = request.user.jobseekerprofile
        resume = Resume.objects.filter(profile=profile).latest('created_at')
        return redirect('resumes:resume-builder')
    except (JobSeekerProfile.DoesNotExist, Resume.DoesNotExist):
        return render(request, 'resumes/resume_dashboard.html')


@login_required
def resume_builder_view(request):
    try:
        profile = request.user.jobseekerprofile
        resume, created = Resume.objects.get_or_create(
            profile=profile, 
            defaults={'title': f"{profile.full_name or request.user.username}'s Resume"}
        )
        
        if created:
            # If a new resume is created, trigger the initial score calculation
            update_resume_score_task.delay(resume.id)

        experiences = Experience.objects.filter(resume=resume).order_by('-start_date')
        educations = Education.objects.filter(resume=resume).order_by('-start_date')
        skills = Skill.objects.filter(resume=resume)
        projects = Project.objects.filter(resume=resume)
        certifications = Certification.objects.filter(resume=resume)
        achievements = Achievement.objects.filter(resume=resume)
        languages = Language.objects.filter(resume=resume)
        hobbies = Hobby.objects.filter(resume=resume)
    except JobSeekerProfile.DoesNotExist:
        JobSeekerProfile.objects.create(user=request.user)
        messages.info(request, "We've created a profile for you to get started.")
        return redirect('resumes:resume-dashboard')

    experience_form = ExperienceForm()
    education_form = EducationForm()
    skill_form = SkillForm()
    project_form = ProjectForm()
    certification_form = CertificationForm()
    achievement_form = AchievementForm()
    language_form = LanguageForm()
    hobby_form = HobbyForm()

    if request.method == 'POST':
        resume.save() # Touches updated_at field
        
        form_map = {
            'add_experience': (ExperienceForm, "Experience"),
            'add_education': (EducationForm, "Education"),
            'add_skill': (SkillForm, "Skill"),
            'add_project': (ProjectForm, "Project"),
            'add_certification': (CertificationForm, "Certification"),
            'add_achievement': (AchievementForm, "Achievement"),
            'add_language': (LanguageForm, "Language"),
            'add_hobby': (HobbyForm, "Hobby"),
        }

        for trigger, (Form, name) in form_map.items():
            if trigger in request.POST:
                form = Form(request.POST)
                if form.is_valid():
                    item = form.save(commit=False); item.resume = resume; item.save()
                    messages.success(request, f"{name} added successfully.")
                    update_resume_score_task.delay(resume.id) # Trigger re-score
                    return redirect('resumes:resume-builder')
                else:
                    # Re-assign the specific form with errors to be displayed
                    if trigger == 'add_experience': experience_form = form
                    elif trigger == 'add_education': education_form = form
                    elif trigger == 'add_skill': skill_form = form
                    elif trigger == 'add_project': project_form = form
                    elif trigger == 'add_certification': certification_form = form
                    elif trigger == 'add_achievement': achievement_form = form
                    elif trigger == 'add_language': language_form = form
                    elif trigger == 'add_hobby': hobby_form = form
    
    # --- Load AI Score & Feedback from DB ---
    score = resume.score
    feedback = resume.feedback
    
    # FIX: Ensure feedback is a list, not a string
    if feedback and isinstance(feedback, str):
        try:
            feedback = json.loads(feedback)
        except json.JSONDecodeError:
            feedback = [] # Fallback to an empty list if JSON is invalid

    context = {
        'resume': resume, 'experiences': experiences, 'educations': educations, 'skills': skills,
        'projects': projects, 'certifications': certifications, 'achievements': achievements,
        'languages': languages, 'hobbies': hobbies,
        'experience_form': experience_form, 'education_form': education_form, 'skill_form': skill_form,
        'project_form': project_form, 'certification_form': certification_form, 'achievement_form': achievement_form,
        'language_form': language_form, 'hobby_form': hobby_form,
        'score': score, 'feedback': feedback
    }
    return render(request, 'resumes/resume_builder.html', context)


@login_required
def upload_resume_view(request):
    if request.method == 'POST':
        form = UploadResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume_file = request.FILES['resume_file']
            if not resume_file.name.lower().endswith(('.pdf', '.docx')):
                messages.error(request, "Invalid file type. Please upload a PDF or DOCX file.")
                return redirect('resumes:resume-dashboard')
            
            fs = FileSystemStorage()
            filename = fs.save(resume_file.name, resume_file)
            full_file_path = fs.path(filename)
            
            # Delegate parsing to Celery task
            parse_resume_task.delay(request.user.id, full_file_path)
            
            # Redirect to the waiting page
            return redirect('resumes:parsing-progress')

    return redirect('resumes:resume-dashboard')

@login_required
def parsing_progress_view(request):
    """Displays the 'parsing in progress' page."""
    # Template is located at resumes/templates/resumes/parsing_in_progress.html
    # When referring to it from Django render(), use the path relative to the
    # templates directory for the app: 'resumes/parsing_in_progress.html'
    return render(request, 'resumes/parsing_in_progress.html')

@login_required
def check_parsing_status_view(request):
    """AJAX endpoint to check if parsing is complete."""
    try:
        profile = request.user.jobseekerprofile
        cache_entry = ParsedResumeCache.objects.get(profile=profile)
        
        # Data is ready, store it in the session and provide redirect URL
        request.session['parsed_resume_data'] = cache_entry.parsed_data
        cache_entry.delete() # Clean up the cache
        
        return JsonResponse({
            'status': 'SUCCESS',
            'redirect_url': reverse('resumes:resume-validate')
        })
    except (JobSeekerProfile.DoesNotExist, ParsedResumeCache.DoesNotExist):
        # Data is not ready yet
        return JsonResponse({'status': 'PENDING'})


@login_required
def validate_resume_data_view(request):
    parsed_data = request.session.get('parsed_resume_data', None)
    if not parsed_data:
        return redirect('resumes:resume-dashboard')

    try:
        profile = request.user.jobseekerprofile
    except JobSeekerProfile.DoesNotExist:
        profile = JobSeekerProfile.objects.create(user=request.user)

    initial_profile_data = parsed_data.get('personal_details', {})
    if parsed_data.get('professional_summary'):
        initial_profile_data['professional_summary'] = parsed_data.get('professional_summary')

    ExperienceFormSet = formset_factory(ExperienceForm, extra=0, can_delete=True)
    EducationFormSet = formset_factory(EducationForm, extra=0, can_delete=True)
    SkillFormSet = formset_factory(SkillForm, extra=0, can_delete=True)
    ProjectFormSet = formset_factory(ProjectForm, extra=0, can_delete=True)
    CertificationFormSet = formset_factory(CertificationForm, extra=0, can_delete=True)
    AchievementFormSet = formset_factory(AchievementForm, extra=0, can_delete=True)
    LanguageFormSet = formset_factory(LanguageForm, extra=0, can_delete=True)
    HobbyFormSet = formset_factory(HobbyForm, extra=0, can_delete=True)

    context = {}
    first_error_section = 'personal'

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, prefix="profile", user=request.user)
        experience_formset = ExperienceFormSet(request.POST, prefix='experience')
        education_formset = EducationFormSet(request.POST, prefix='education')
        skill_formset = SkillFormSet(request.POST, prefix='skill')
        project_formset = ProjectFormSet(request.POST, prefix='project')
        certification_formset = CertificationFormSet(request.POST, prefix='certification')
        achievement_formset = AchievementFormSet(request.POST, prefix='achievement')
        language_formset = LanguageFormSet(request.POST, prefix='language')
        hobby_formset = HobbyFormSet(request.POST, prefix='hobby')

        all_formsets_valid = all([
            fs.is_valid() for fs in [
                experience_formset, education_formset, skill_formset, project_formset,
                certification_formset, achievement_formset, language_formset, hobby_formset
            ]
        ])

        if profile_form.is_valid() and all_formsets_valid:
            profile = profile_form.save()
            resume, created = Resume.objects.update_or_create(
                profile=profile,
                defaults={'title': f"{profile.full_name or 'My'}'s Resume"}
            )
            for related_set_name in ['experience_set', 'education_set', 'skill_set', 'project_set', 'certification_set', 'achievement_set', 'language_set', 'hobby_set']:
                if hasattr(resume, related_set_name):
                    getattr(resume, related_set_name).all().delete()
            
            for formset in [experience_formset, education_formset, skill_formset, project_formset, certification_formset, achievement_formset, language_formset, hobby_formset]:
                for form in formset:
                    if form.has_changed() and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False); item.resume = resume; item.save()

            del request.session['parsed_resume_data']
            messages.success(request, "Your resume has been built from the uploaded file!")
            update_resume_score_task.delay(resume.id) # Trigger initial score
            return redirect('resumes:resume-builder')
        else:
            messages.error(request, "Please correct the errors below before saving.")
            # Build the context so the template can display the bound forms and errors
            # Determine which section should be opened first (the first with errors)
            validation_errors = {}
            # Profile form errors
            if profile_form.errors:
                try:
                    validation_errors['personal'] = profile_form.errors.get_json_data()
                except Exception:
                    validation_errors['personal'] = str(profile_form.errors)

            # Helper to collect errors for a formset
            def collect_formset_errors(prefix, fs):
                fs_errors = {}
                # non_form_errors
                non_form = list(fs.non_form_errors()) if hasattr(fs, 'non_form_errors') else []
                if non_form:
                    fs_errors['non_form_errors'] = non_form
                forms_list = []
                for form in fs:
                    if form.errors:
                        try:
                            forms_list.append(form.errors.get_json_data())
                        except Exception:
                            forms_list.append(str(form.errors))
                    else:
                        forms_list.append({})
                if forms_list:
                    fs_errors['forms'] = forms_list
                return fs_errors

            # Collect errors for each formset
            fs_map = {
                'experience': experience_formset,
                'education': education_formset,
                'project': project_formset,
                'certification': certification_formset,
                'achievement': achievement_formset,
                'language': language_formset,
                'hobby': hobby_formset,
                'skill': skill_formset,
            }

            for key, fs in fs_map.items():
                errs = collect_formset_errors(key, fs)
                if errs:
                    validation_errors[key] = errs

            # Decide first_error_section (priority: personal, then formset order)
            first_error_section = 'personal' if validation_errors.get('personal') else None
            if not first_error_section:
                for k in ['experience', 'education', 'project', 'certification', 'achievement', 'language', 'hobby', 'skill']:
                    if k in validation_errors:
                        first_error_section = k
                        break
            if not first_error_section:
                first_error_section = 'personal'

            # Rebuild formset_data for template using the bound formsets
            formset_data = {
                'experience': {'title': 'Experience', 'formset': experience_formset},
                'education': {'title': 'Education', 'formset': education_formset},
                'project': {'title': 'Projects', 'formset': project_formset},
                'certification': {'title': 'Certifications', 'formset': certification_formset},
                'achievement': {'title': 'Achievements', 'formset': achievement_formset},
                'language': {'title': 'Languages', 'formset': language_formset},
                'hobby': {'title': 'Hobbies', 'formset': hobby_formset},
            }

            context.update({
                'profile_form': profile_form,
                'skill_formset': skill_formset,
                'formset_data': formset_data,
                'first_error_section': first_error_section,
                'validation_errors_json': json.dumps(validation_errors),
            })

            return render(request, 'resumes/validate_resume.html', context)
            
    else:
        profile_form = ProfileUpdateForm(instance=profile, initial=initial_profile_data, prefix="profile", user=request.user)
        experience_formset = ExperienceFormSet(initial=parsed_data.get('experience', []), prefix='experience')
        education_formset = EducationFormSet(initial=parsed_data.get('education', []), prefix='education')
        project_formset = ProjectFormSet(initial=parsed_data.get('projects', []), prefix='project')
        certification_formset = CertificationFormSet(initial=parsed_data.get('certifications', []), prefix='certification')
        achievement_formset = AchievementFormSet(initial=parsed_data.get('achievements', []), prefix='achievement')
        language_formset = LanguageFormSet(initial=parsed_data.get('languages', []), prefix='language')
        skills_initial = [{'name': s.get('name'), 'category': s.get('category', 'Other')} for s in parsed_data.get('skills', []) if s.get('name')]
        skill_formset = SkillFormSet(initial=skills_initial, prefix='skill')
        hobbies_initial = [{'name': h} for h in parsed_data.get('hobbies', []) if h]
        hobby_formset = HobbyFormSet(initial=hobbies_initial, prefix='hobby')

    formset_data = {
        'experience': {'title': 'Experience', 'formset': experience_formset},
        'education': {'title': 'Education', 'formset': education_formset},
        'project': {'title': 'Projects', 'formset': project_formset},
        'certification': {'title': 'Certifications', 'formset': certification_formset},
        'achievement': {'title': 'Achievements', 'formset': achievement_formset},
        'language': {'title': 'Languages', 'formset': language_formset},
        'hobby': {'title': 'Hobbies', 'formset': hobby_formset},
    }

    context.update({
        'profile_form': profile_form,
        'skill_formset': skill_formset,
        'formset_data': formset_data,
        'first_error_section': first_error_section,
    })

    return render(request, 'resumes/validate_resume.html', context)


# --- Generic Edit and Delete Views ---
@login_required
def edit_item(request, model_name, pk):
    model_map = {
        'experience': (Experience, ExperienceForm), 'education': (Education, EducationForm),
        'skill': (Skill, SkillForm), 'project': (Project, ProjectForm),
        'certification': (Certification, CertificationForm), 'achievement': (Achievement, AchievementForm),
        'language': (Language, LanguageForm), 'hobby': (Hobby, HobbyForm),
    }
    Model, Form = model_map.get(model_name)
    item = get_object_or_404(Model, pk=pk, resume__profile__user=request.user)
    title = f'Edit {model_name.replace("_", " ").title()}'
    
    if request.method == 'POST':
        form = Form(request.POST, instance=item)
        if form.is_valid():
            form.save()
            update_resume_score_task.delay(item.resume.id) # Trigger re-score
            messages.success(request, f'{model_name.replace("_", " ").title()} updated successfully.')
            return redirect('resumes:resume-builder')
    else:
        form = Form(instance=item)
    
    return render(request, 'resumes/edit_item.html', {'form': form, 'title': title})

@login_required
def delete_item(request, model_name, pk):
    model_map = {'experience': Experience, 'education': Education, 'skill': Skill, 'project': Project, 
                 'certification': Certification, 'achievement': Achievement, 'language': Language, 'hobby': Hobby}
    Model = model_map.get(model_name)
    item = get_object_or_404(Model, pk=pk, resume__profile__user=request.user)
    
    if request.method == 'POST':
        resume_id = item.resume.id
        item.delete()
        update_resume_score_task.delay(resume_id) # Trigger re-score
        
        if "HTTP_X_REQUESTED_WITH" in request.META and request.META["HTTP_X_REQUESTED_WITH"] == "XMLHttpRequest":
            return JsonResponse({'status': 'success', 'message': f'{model_name.title()} deleted successfully.'})
        
        messages.success(request, f'{model_name.replace("_", " ").title()} deleted successfully.')
        return redirect('resumes:resume-builder')

    # For non-POST requests to this URL, just redirect
    return redirect('resumes:resume-builder')
    
@login_required
def enhance_description_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text_to_enhance = data.get('text')
            context = data.get('context')
            if not text_to_enhance:
                return JsonResponse({'error': 'No text provided.'}, status=400)

            enhanced_text = enhance_text_with_gemini(text_to_enhance, context)
            if enhanced_text:
                return JsonResponse({'enhanced_text': enhanced_text})
            else:
                return JsonResponse({'error': 'Failed to enhance text.'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def download_resume_pdf(request, resume_id, template_name):
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    
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
        pdf_bytes = html_obj.write_pdf()
    except Exception as e:
        return HttpResponse('PDF generation (WeasyPrint) failed: ' + str(e) + '<pre>' + html + '</pre>')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.profile.full_name}_resume.pdf"'
    return response

