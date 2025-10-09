from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
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
from .parser import enhance_text_with_gemini

# --- Main Views ---
@login_required
def resume_dashboard_view(request):
    try:
        profile = request.user.jobseekerprofile
        resume = Resume.objects.filter(profile=profile).latest('created_at')
        
        from .templatetags.resume_extras import get_resume_completeness_errors
        if not get_resume_completeness_errors(resume):
             return redirect('resumes:resume-builder')

    except (JobSeekerProfile.DoesNotExist, Resume.DoesNotExist):
        pass

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
            transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
        
        if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return handle_ajax_request(request, resume)

        # Prepare context for the initial page load
        resume_sections = [
            {'name': 'experience', 'title': 'Experience', 'form': ExperienceForm(), 'items': Experience.objects.filter(resume=resume).order_by('-start_date')},
            {'name': 'education', 'title': 'Education', 'form': EducationForm(), 'items': Education.objects.filter(resume=resume).order_by('-start_date')},
            {'name': 'skill', 'title': 'Skills', 'form': SkillForm(), 'items': Skill.objects.filter(resume=resume)},
            {'name': 'project', 'title': 'Projects', 'form': ProjectForm(), 'items': Project.objects.filter(resume=resume)},
            {'name': 'certification', 'title': 'Certifications', 'form': CertificationForm(), 'items': Certification.objects.filter(resume=resume)},
            {'name': 'achievement', 'title': 'Achievements', 'form': AchievementForm(), 'items': Achievement.objects.filter(resume=resume)},
            {'name': 'language', 'title': 'Languages', 'form': LanguageForm(), 'items': Language.objects.filter(resume=resume)},
            {'name': 'hobby', 'title': 'Hobbies', 'form': HobbyForm(), 'items': Hobby.objects.filter(resume=resume)},
        ]
        
        score = resume.score
        feedback = resume.feedback
        if feedback and isinstance(feedback, str):
            try: feedback = json.loads(feedback)
            except json.JSONDecodeError: feedback = []

        context = {
            'resume': resume,
            'score': score, 
            'feedback': json.dumps(feedback),
            'resume_sections': resume_sections,
        }
        return render(request, 'resumes/resume_builder.html', context)

    except JobSeekerProfile.DoesNotExist:
        JobSeekerProfile.objects.create(user=request.user)
        messages.info(request, "We've created a profile for you to get started.")
        return redirect('resumes:resume-dashboard')


def handle_ajax_request(request, resume):
    action = request.POST.get('action')
    model_name = request.POST.get('model_name')
    pk = request.POST.get('pk')

    model_map = {
        'experience': (Experience, ExperienceForm), 'education': (Education, EducationForm),
        'skill': (Skill, SkillForm), 'project': (Project, ProjectForm),
        'certification': (Certification, CertificationForm), 'achievement': (Achievement, AchievementForm),
        'language': (Language, LanguageForm), 'hobby': (Hobby, HobbyForm),
        'personal_details': (JobSeekerProfile, ProfileUpdateForm),
    }

    if model_name not in model_map:
        return JsonResponse({'status': 'error', 'message': 'Invalid model specified.'}, status=400)

    Model, Form = model_map[model_name]
    is_profile = (model_name == 'personal_details')

    if action == 'add':
        if is_profile: return JsonResponse({'status': 'error', 'message': 'Cannot add a profile.'}, status=400)
        form = Form(request.POST)
        if form.is_valid():
            item = form.save(commit=False); item.resume = resume; item.save()
            resume.score = None; resume.save()
            transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
            item_html = render_to_string(f'resumes/partials/{model_name}_item.html', {'item': item})
            return JsonResponse({'status': 'success', 'item_html': item_html, 'section': model_name})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)
    
    elif action == 'get_edit_form':
        item = get_object_or_404(Model, pk=pk)
        if not is_profile and item.resume != resume: return JsonResponse({'status': 'error'}, status=403)
        if is_profile and item.user != request.user: return JsonResponse({'status': 'error'}, status=403)

        form_kwargs = {'instance': item}
        if is_profile: form_kwargs['user'] = request.user
        
        form = Form(**form_kwargs)
        template_name = f'resumes/partials/{"personal_details" if is_profile else model_name}_form.html'
        form_html = render_to_string(template_name, {'form': form, 'pk': pk}, request=request)
        return JsonResponse({'status': 'success', 'form_html': form_html})

    elif action == 'update':
        item = get_object_or_404(Model, pk=pk)
        if not is_profile and item.resume != resume: return JsonResponse({'status': 'error'}, status=403)
        if is_profile and item.user != request.user: return JsonResponse({'status': 'error'}, status=403)
        
        form_kwargs = {'instance': item, 'data': request.POST, 'files': request.FILES}
        if is_profile: form_kwargs['user'] = request.user

        form = Form(**form_kwargs)
        if form.is_valid():
            item = form.save()
            resume.score = None; resume.save()
            transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
            
            if is_profile:
                resume.refresh_from_db()

            context = {'item': item} if not is_profile else {'resume': resume}
            template_name = f'resumes/partials/{"personal_details_section" if is_profile else model_name + "_item"}.html'

            item_html = render_to_string(template_name, context, request=request)
            return JsonResponse({'status': 'success', 'item_html': item_html, 'pk': pk, 'new_title': resume.title})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    elif action == 'delete':
        if is_profile: return JsonResponse({'status': 'error', 'message': 'Cannot delete a profile.'}, status=400)
        item = get_object_or_404(Model, pk=pk, resume=resume)
        item.delete()
        resume.score = None; resume.save()
        transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
        return JsonResponse({'status': 'success', 'section': model_name})

    return JsonResponse({'status': 'error', 'message': 'Invalid action.'}, status=400)


# --- File Upload and Parsing ---
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

            parse_resume_task.delay(request.user.id, full_file_path)

            return redirect('resumes:parsing-progress')

    return redirect('resumes:resume-dashboard')

@login_required
def parsing_progress_view(request):
    return render(request, 'resumes/parsing_in_progress.html')

@login_required
def check_parsing_status_view(request):
    try:
        profile = request.user.jobseekerprofile
        cache_entry = ParsedResumeCache.objects.get(profile=profile)

        request.session['parsed_resume_data'] = cache_entry.parsed_data
        cache_entry.delete()

        return JsonResponse({
            'status': 'SUCCESS',
            'redirect_url': reverse('resumes:resume-validate')
        })
    except (JobSeekerProfile.DoesNotExist, ParsedResumeCache.DoesNotExist):
        return JsonResponse({'status': 'PENDING'})


@login_required
def validate_resume_data_view(request):
    from django.forms import formset_factory
    parsed_data = request.session.get('parsed_resume_data')
    if not parsed_data:
        messages.warning(request, "Your session has expired. Please upload your resume again.")
        return redirect('resumes:resume-dashboard')

    profile = get_object_or_404(JobSeekerProfile, user=request.user)

    formset_classes = {
        'experience': formset_factory(ExperienceForm, extra=0, can_delete=True),
        'education': formset_factory(EducationForm, extra=0, can_delete=True),
        'skill': formset_factory(SkillForm, extra=0, can_delete=True),
        'project': formset_factory(ProjectForm, extra=0, can_delete=True),
        'certification': formset_factory(CertificationForm, extra=0, can_delete=True),
        'achievement': formset_factory(AchievementForm, extra=0, can_delete=True),
        'language': formset_factory(LanguageForm, extra=0, can_delete=True),
        'hobby': formset_factory(HobbyForm, extra=0, can_delete=True),
    }

    if request.method == 'POST':
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile, prefix="profile", user=request.user)
        
        formsets = {key: fs_class(request.POST, prefix=key) for key, fs_class in formset_classes.items()}

        is_profile_valid = profile_form.is_valid()
        are_formsets_valid = all(fs.is_valid() for fs in formsets.values())

        if is_profile_valid and are_formsets_valid:
            profile = profile_form.save()
            resume, _ = Resume.objects.update_or_create(profile=profile, defaults={'title': f"{profile.full_name or 'My'}'s Resume", 'score': None})
            
            for related_set in ['experience_set', 'education_set', 'skill_set', 'project_set', 'certification_set', 'achievement_set', 'language_set', 'hobby_set']:
                getattr(resume, related_set).all().delete()
            
            for formset in formsets.values():
                for form in formset:
                    if form.is_valid() and form.has_changed() and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.resume = resume
                        item.save()

            del request.session['parsed_resume_data']
            messages.success(request, "Your resume has been built successfully!")
            transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
            return redirect('resumes:resume-builder')
        else:
            messages.error(request, "Please correct the errors highlighted in red below.")
            
            first_error_section = 'personal'
            if profile_form.errors:
                first_error_section = 'personal'
            else:
                for key, fs in formsets.items():
                    if fs.errors or fs.non_form_errors():
                        first_error_section = key
                        break
            
            context = { 'profile_form': profile_form, 'first_error_section': first_error_section }
            context.update({f'{key}_formset': fs for key, fs in formsets.items()})
            return render(request, 'resumes/validate_resume.html', context)

    else:
        initial_profile_data = parsed_data.get('personal_details', {})
        if parsed_data.get('professional_summary'):
            initial_profile_data['professional_summary'] = parsed_data.get('professional_summary')
        
        profile_form = ProfileUpdateForm(instance=profile, initial=initial_profile_data, prefix="profile", user=request.user)
        
        initial_data = {
            'experience': parsed_data.get('experience', []),
            'education': parsed_data.get('education', []),
            'project': parsed_data.get('projects', []),
            'certification': parsed_data.get('certifications', []),
            'achievement': parsed_data.get('achievements', []),
            'language': parsed_data.get('languages', []),
            'skill': [{'name': s.get('name'), 'category': s.get('category', 'Other')} for s in parsed_data.get('skills', []) if s.get('name')],
            'hobby': [{'name': h} for h in parsed_data.get('hobbies', []) if h],
        }
        
        formsets = {key: fs_class(initial=initial_data.get(key, []), prefix=key) for key, fs_class in formset_classes.items()}

        context = { 'profile_form': profile_form, 'first_error_section': 'personal' }
        context.update({f'{key}_formset': fs for key, fs in formsets.items()})
        return render(request, 'resumes/validate_resume.html', context)


# --- Other Views ---
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
    """
    Generates and serves a PDF resume.
    This view now pre-processes descriptions into bullet points.
    """
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    
    # Pre-process descriptions to create bullet points
    def process_description(items):
        processed_items = []
        for item in items:
            if item.description:
                clean_desc = '\n'.join(line.lstrip('*-• ') for line in item.description.splitlines())
                item.description_points = [point.strip() for point in clean_desc.splitlines() if point.strip()]
            else:
                item.description_points = []
            processed_items.append(item)
        return processed_items

    experiences = Experience.objects.filter(resume=resume).order_by('-start_date')
    projects = Project.objects.filter(resume=resume)

    # Group skills by category for better presentation
    skills_by_category = {}
    skills_qs = Skill.objects.filter(resume=resume).order_by('category')
    for skill in skills_qs:
        category = skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill.name)

    context = {
        'resume': resume,
        'experiences': process_description(experiences),
        'projects': process_description(projects),
        'educations': Education.objects.filter(resume=resume).order_by('-start_date'),
        'skills_by_category': skills_by_category,
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
        messages.error(request, 'PDF generation service is currently unavailable. Please try again later.')
        return redirect('resumes:resume-builder')

    try:
        html_obj = HTML(string=html, base_url=request.build_absolute_uri('/'))
        # Set a standard A4 page margin for all templates
        pdf_bytes = html_obj.write_pdf(stylesheets=[CSS(string='@page { size: A4; margin: 1.5cm }')])
    except Exception as e:
        # Provide a more user-friendly error
        messages.error(request, f'An error occurred during PDF generation: {e}')
        return redirect('resumes:resume-builder')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.profile.full_name}_resume.pdf"'
    return response

@login_required
def check_score_status_view(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    if resume.score is not None:
        feedback = resume.feedback
        if isinstance(feedback, str):
            try:
                feedback = json.loads(feedback)
            except json.JSONDecodeError:
                feedback = ["Could not load feedback."]
        
        return JsonResponse({
            'status': 'SUCCESS',
            'score': resume.score,
            'feedback': feedback,
        })
    else:
        return JsonResponse({'status': 'PENDING'})
