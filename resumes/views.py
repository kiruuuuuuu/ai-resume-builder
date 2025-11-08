from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string, get_template
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
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
        # Optimize query with select_related
        resume = Resume.objects.filter(profile=profile).select_related('profile').latest('created_at')
        
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
            {'name': 'experience', 'title': 'Experience', 'form': ExperienceForm(), 'items': Experience.objects.filter(resume=resume).select_related('resume').order_by('-start_date')},
            {'name': 'education', 'title': 'Education', 'form': EducationForm(), 'items': Education.objects.filter(resume=resume).select_related('resume').order_by('-start_date')},
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
            try: 
                feedback = json.loads(feedback)
            except json.JSONDecodeError: 
                feedback = []
        elif feedback is None:
            feedback = []

        context = {
            'resume': resume,
            'score': score, 
            'feedback': json.dumps(feedback) if feedback else '[]',
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
            # Trigger match score recalculation for all jobs
            from jobs.tasks import calculate_and_save_match_score_task
            from jobs.models import JobPosting
            job_ids = list(JobPosting.objects.filter(
                Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
            ).values_list('id', flat=True))
            resume_id = resume.id
            for job_id in job_ids:
                transaction.on_commit(lambda jid=job_id, rid=resume_id: calculate_and_save_match_score_task.delay(rid, jid))
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
            # Trigger match score recalculation for all jobs
            from jobs.tasks import calculate_and_save_match_score_task
            from jobs.models import JobPosting
            job_ids = list(JobPosting.objects.filter(
                Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
            ).values_list('id', flat=True))
            resume_id = resume.id
            for job_id in job_ids:
                transaction.on_commit(lambda jid=job_id, rid=resume_id: calculate_and_save_match_score_task.delay(rid, jid))
            
            if is_profile:
                resume.refresh_from_db()

            context = {'item': item} if not is_profile else {'resume': resume}
            template_name = f'resumes/partials/{"personal_details_section" if is_profile else model_name + "_item"}.html'

            item_html = render_to_string(template_name, context, request=request)
            return JsonResponse({'status': 'success', 'item_html': item_html, 'pk': pk, 'new_title': resume.title})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors}, status=400)

    elif action == 'delete':
        if is_profile: 
            return JsonResponse({'status': 'error', 'message': 'Cannot delete a profile.'}, status=400)
        
        if not pk:
            return JsonResponse({'status': 'error', 'message': 'Item ID is required.'}, status=400)
        
        try:
            item = Model.objects.get(pk=pk, resume=resume)
        except Model.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Item not found or you do not have permission to delete it.'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Error deleting item: {str(e)}'}, status=500)
        
        try:
            item.delete()
            resume.score = None
            resume.save()
            transaction.on_commit(lambda: update_resume_score_task.delay(resume.id))
            # Trigger match score recalculation for all jobs
            from jobs.tasks import calculate_and_save_match_score_task
            from jobs.models import JobPosting
            job_ids = list(JobPosting.objects.filter(
                Q(application_deadline__gte=timezone.now()) | Q(application_deadline__isnull=True)
            ).values_list('id', flat=True))
            resume_id = resume.id
            for job_id in job_ids:
                transaction.on_commit(lambda jid=job_id, rid=resume_id: calculate_and_save_match_score_task.delay(rid, jid))
            return JsonResponse({'status': 'success', 'section': model_name})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': f'Failed to delete item: {str(e)}'}, status=500)

    elif action == 'get_item_html':
        item = get_object_or_404(Model, pk=pk)
        if not is_profile and item.resume != resume: return JsonResponse({'status': 'error'}, status=403)
        if is_profile and item.user != request.user: return JsonResponse({'status': 'error'}, status=403)

        context = {'item': item} if not is_profile else {'resume': resume}
        template_name = f'resumes/partials/{"personal_details_section" if is_profile else model_name + "_item"}.html'
        item_html = render_to_string(template_name, context, request=request)
        return JsonResponse({'status': 'success', 'item_html': item_html})

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
            
            # Validate file size (max 10MB for resume files)
            max_size = 10 * 1024 * 1024  # 10MB
            if resume_file.size > max_size:
                messages.error(request, "File size exceeds 10MB limit. Please upload a smaller file.")
                return redirect('resumes:resume-dashboard')

            # Read file content into memory and encode as base64
            # This allows the file to be passed to Celery worker in a separate container
            import base64
            file_content = resume_file.read()
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            filename = resume_file.name

            # Pass file content and filename to Celery task
            parse_resume_task.delay(request.user.id, filename, file_content_b64)

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

        # Validate profile form
        is_profile_valid = profile_form.is_valid()
        
        # Validate all formsets - need to call is_valid() to trigger validation
        # This will validate all forms in each formset and populate errors
        are_formsets_valid = True
        for fs in formsets.values():
            fs_valid = fs.is_valid()
            if not fs_valid:
                are_formsets_valid = False
            else:
                # Even if formset is valid, check individual forms for errors
                # (in case formset validation passed but individual forms have errors)
                for form in fs:
                    # Skip deleted forms
                    if form.cleaned_data and form.cleaned_data.get('DELETE', False):
                        continue
                    if form.errors:
                        are_formsets_valid = False
                        break

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
            
            # Determine first error section - check both formset-level and individual form errors
            first_error_section = 'personal'
            has_any_errors = False
            
            if profile_form.errors:
                first_error_section = 'personal'
                has_any_errors = True
            else:
                for key, fs in formsets.items():
                    # Check for formset-level errors
                    if fs.non_form_errors():
                        first_error_section = key
                        has_any_errors = True
                        break
                    # Check for individual form errors
                    if any(form.errors for form in fs):
                        first_error_section = key
                        has_any_errors = True
                        break
            
            # Count total errors for display - count actual error messages
            total_errors = 0
            # Count profile form errors (each field can have multiple error messages)
            for field_errors in profile_form.errors.values():
                total_errors += len(field_errors)
            
            # Count formset errors
            for fs in formsets.values():
                # Count formset-level errors
                total_errors += len(fs.non_form_errors())
                # Count individual form errors (each field can have multiple error messages)
                for form in fs:
                    for field_errors in form.errors.values():
                        total_errors += len(field_errors)
            
            context = { 
                'profile_form': profile_form, 
                'first_error_section': first_error_section,
                'has_any_errors': has_any_errors,
                'total_errors': total_errors,
            }
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

        context = { 
            'profile_form': profile_form, 
            'first_error_section': 'personal',
            'has_any_errors': False,
            'total_errors': 0,
        }
        context.update({f'{key}_formset': fs for key, fs in formsets.items()})
        return render(request, 'resumes/validate_resume.html', context)


# --- Other Views ---
# Rate limiting (optional - install django-ratelimit for rate limiting)
try:
    from django_ratelimit.decorators import ratelimit
    from django_ratelimit.exceptions import Ratelimited
    RATELIMIT_AVAILABLE = True
except ImportError:
    # Fallback decorator if django-ratelimit is not installed
    def ratelimit(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    RATELIMIT_AVAILABLE = False

@ratelimit(key='ip', rate='20/m', method='POST', block=True)
@login_required
def enhance_description_api(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            text_to_enhance = data.get('text')
            context = data.get('context')
            
            # Sanitize input
            from core.utils import sanitize_text
            if text_to_enhance:
                text_to_enhance = sanitize_text(text_to_enhance)
            
            if not text_to_enhance:
                return JsonResponse({'error': 'No text provided.'}, status=400)

            # Define character limits for validation
            char_limits = {
                'experience_description': 500,
                'professional_summary': 600,
                'project_description': 400,
            }
            max_chars = char_limits.get(context, 500)
            original_length = len(text_to_enhance) if text_to_enhance else 0

            enhanced_text = enhance_text_with_gemini(text_to_enhance, context)
            if enhanced_text:
                # Check if truncation occurred
                was_truncated = len(enhanced_text) > max_chars
                if was_truncated:
                    # Final safety check - truncate if still over limit
                    enhanced_text = enhanced_text[:max_chars].rsplit(' ', 1)[0]
                
                response_data = {
                    'enhanced_text': enhanced_text,
                    'was_truncated': len(enhanced_text) >= max_chars - 10,  # Warn if close to limit
                }
                return JsonResponse(response_data)
            else:
                return JsonResponse({'error': 'Failed to enhance text.'}, status=500)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@login_required
def download_resume_pdf(request, resume_id, template_name):
    """
    Initiates async PDF generation and returns task ID.
    For backward compatibility, if async is disabled or table doesn't exist, falls back to sync generation.
    """
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    
    # Get accent color from query parameter (default to blue)
    accent_color = request.GET.get('accent_color', 'blue')
    
    # Check if async is enabled (Celery available) and table exists
    use_async = False
    try:
        from .models import ResumePDFGeneration
        from .tasks import generate_resume_pdf_task
        from django.db import connection
        
        # Check if table exists (works for both SQLite and PostgreSQL)
        table_name = ResumePDFGeneration._meta.db_table
        table_exists = False
        
        with connection.cursor() as cursor:
            if 'sqlite' in connection.vendor:
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name=?
                """, [table_name])
            elif 'postgresql' in connection.vendor:
                cursor.execute("""
                    SELECT tablename FROM pg_tables 
                    WHERE schemaname = 'public' AND tablename = %s
                """, [table_name])
            else:
                # For other databases, try to query the table (will fail if it doesn't exist)
                try:
                    ResumePDFGeneration.objects.first()
                    table_exists = True
                except:
                    table_exists = False
            
            if not table_exists:
                table_exists = cursor.fetchone() is not None
        
        # Check if Celery is configured
        celery_configured = bool(getattr(settings, 'CELERY_BROKER_URL', None))
        
        use_async = table_exists and celery_configured
    except Exception:
        # If any error occurs (ImportError, table doesn't exist, etc.), fall back to sync
        use_async = False
    
    if use_async:
        try:
            # Create PDF generation record
            pdf_gen = ResumePDFGeneration.objects.create(
                resume=resume,
                template_name=template_name,
                accent_color=accent_color,
                status='pending'
            )
            
            # Trigger async task
            base_url = request.build_absolute_uri('/')
            task = generate_resume_pdf_task.delay(pdf_gen.id, base_url)
            pdf_gen.task_id = task.id
            pdf_gen.save(update_fields=['task_id'])
            
            # Return JSON response with task ID for frontend polling
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
                return JsonResponse({
                    'status': 'pending',
                    'task_id': task.id,
                    'pdf_generation_id': pdf_gen.id,
                    'message': 'PDF generation started. Please wait...'
                })
            
            # For regular requests, redirect to status page or show message
            messages.info(request, 'PDF generation started. You will be notified when it\'s ready.')
            return redirect('resumes:resume-builder')
        except Exception as e:
            # If async fails for any reason, fall back to sync
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Async PDF generation failed, falling back to sync: {e}")
            return _generate_pdf_sync(request, resume, template_name, accent_color)
    else:
        # Fallback to synchronous generation for backward compatibility
        return _generate_pdf_sync(request, resume, template_name, accent_color)

def _generate_pdf_sync(request, resume, template_name, accent_color):
    """Synchronous PDF generation (fallback when async is not available)."""
    # Color mapping
    color_map = {
        'blue': '#3498db',
        'teal': '#14b8a6',
        'indigo': '#6366f1',
        'purple': '#a855f7',
        'red': '#ef4444',
        'graphite': '#475569',
    }
    
    accent_color_hex = color_map.get(accent_color, '#3498db')

    context = _get_resume_context(resume)
    context['accent_color'] = accent_color_hex
    
    template_path = f'resumes/resume_pdf_{template_name}.html'
    template = get_template(template_path)
    html = template.render(context)

    if not WEASY_AVAILABLE:
        messages.error(request, 'PDF generation service is currently unavailable. Please try again later.')
        return redirect('resumes:resume-builder')

    try:
        html_obj = HTML(string=html, base_url=request.build_absolute_uri('/'))
        # Set template-specific margins to match the template's @page rules
        if template_name == 'modern':
            page_css = '@page { size: A4; margin: 0 }'
        elif template_name == 'creative':
            page_css = '@page { size: A4; margin: 0.5cm }'
        else:  # classic and professional
            page_css = '@page { size: A4; margin: 1.5cm }'
        pdf_bytes = html_obj.write_pdf(stylesheets=[CSS(string=page_css)])
    except Exception as e:
        # Log the full error for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f'PDF generation error for template {template_name}: {e}', exc_info=True)
        # Provide a more user-friendly error
        messages.error(request, f'An error occurred during PDF generation: {e}')
        return redirect('resumes:resume-builder')

    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{resume.profile.full_name}_resume.pdf"'
    return response

@login_required
def check_pdf_status(request, pdf_generation_id):
    """Check the status of a PDF generation task."""
    from .models import ResumePDFGeneration
    
    pdf_gen = get_object_or_404(ResumePDFGeneration, id=pdf_generation_id, resume__profile__user=request.user)
    
    response_data = {
        'status': pdf_gen.status,
        'pdf_generation_id': pdf_gen.id,
    }
    
    if pdf_gen.status == 'completed' and pdf_gen.pdf_file:
        response_data['download_url'] = pdf_gen.pdf_file.url
        response_data['filename'] = pdf_gen.pdf_file.name.split('/')[-1]
    elif pdf_gen.status == 'failed':
        response_data['error'] = pdf_gen.error_message or 'PDF generation failed.'
    
    return JsonResponse(response_data)

@login_required
def download_generated_pdf(request, pdf_generation_id):
    """Download a completed PDF."""
    from .models import ResumePDFGeneration
    from django.http import FileResponse
    
    pdf_gen = get_object_or_404(
        ResumePDFGeneration, 
        id=pdf_generation_id, 
        resume__profile__user=request.user,
        status='completed'
    )
    
    if not pdf_gen.pdf_file:
        messages.error(request, 'PDF file not found.')
        return redirect('resumes:resume-builder')
    
    response = FileResponse(pdf_gen.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{pdf_gen.resume.profile.full_name}_resume.pdf"'
    return response

def _get_resume_context(resume):
    """Helper function to prepare resume context for templates."""
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

    experiences = Experience.objects.filter(resume=resume).select_related('resume').order_by('-start_date')
    projects = Project.objects.filter(resume=resume)

    # Group skills by category for better presentation
    skills_by_category = {}
    skills_qs = Skill.objects.filter(resume=resume).order_by('category')
    for skill in skills_qs:
        category = skill.get_category_display()
        if category not in skills_by_category:
            skills_by_category[category] = []
        skills_by_category[category].append(skill.name)

    return {
        'resume': resume,
        'experiences': process_description(experiences),
        'projects': process_description(projects),
        'educations': Education.objects.filter(resume=resume).select_related('resume').order_by('-start_date'),
        'skills_by_category': skills_by_category,
        'certifications': Certification.objects.filter(resume=resume),
        'achievements': Achievement.objects.filter(resume=resume),
        'languages': Language.objects.filter(resume=resume),
        'hobbies': [hobby.name for hobby in Hobby.objects.filter(resume=resume)],
        'settings': settings,
    }

@login_required
def get_preview_html_view(request, resume_id):
    """Returns HTML preview of resume for live preview panel."""
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    
    # Get template and color from query parameters
    template_name = request.GET.get('template', 'classic')
    accent_color = request.GET.get('accent_color', 'indigo')
    
    # Validate template name
    valid_templates = ['classic', 'modern', 'professional', 'creative']
    if template_name not in valid_templates:
        template_name = 'classic'
    
    # Color mapping
    color_map = {
        'blue': '#3498db',
        'teal': '#14b8a6',
        'indigo': '#6366f1',
        'purple': '#a855f7',
        'red': '#ef4444',
        'graphite': '#475569',
    }
    accent_color_hex = color_map.get(accent_color, '#6366f1')
    
    context = _get_resume_context(resume)
    context['accent_color'] = accent_color_hex
    
    # Use the selected template for preview
    template_path = f'resumes/resume_pdf_{template_name}.html'
    preview_html = render_to_string(template_path, context, request=request)
    
    return JsonResponse({'status': 'success', 'preview_html': preview_html})

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
        elif feedback is None:
            feedback = []
        
        # Ensure feedback is always a list
        if not isinstance(feedback, list):
            feedback = [str(feedback)] if feedback else []
        
        return JsonResponse({
            'status': 'SUCCESS',
            'score': resume.score,
            'feedback': feedback,
        })
    else:
        return JsonResponse({'status': 'PENDING'})

@login_required
def dismiss_welcome_view(request):
    """Mark welcome modal as dismissed in session."""
    request.session['show_welcome_modal'] = False
    return JsonResponse({'status': 'success'})

@login_required
def preview_resume_view(request, resume_id):
    """Dedicated fullscreen preview page showing only resume content."""
    resume = get_object_or_404(Resume, id=resume_id, profile__user=request.user)
    
    # Get template and color from query parameters
    template_name = request.GET.get('template', 'professional')
    accent_color = request.GET.get('accent_color', 'indigo')
    
    # Validate template name
    valid_templates = ['classic', 'modern', 'professional', 'creative']
    if template_name not in valid_templates:
        template_name = 'professional'
    
    # Color mapping
    color_map = {
        'blue': '#3498db',
        'teal': '#14b8a6',
        'indigo': '#6366f1',
        'purple': '#a855f7',
        'red': '#ef4444',
        'graphite': '#475569',
    }
    accent_color_hex = color_map.get(accent_color, '#6366f1')
    
    context = _get_resume_context(resume)
    context['accent_color'] = accent_color_hex
    context['template_name'] = template_name
    context['selected_color'] = accent_color
    context['color_options'] = list(color_map.keys())
    context['template_options'] = valid_templates
    
    # Render the resume template content
    template_path = f'resumes/resume_pdf_{template_name}.html'
    resume_html = render_to_string(template_path, context, request=request)
    
    # Extract styles and body content properly - ensure ALL content is preserved
    import re
    
    try:
        # Try using BeautifulSoup for better HTML parsing
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resume_html, 'html.parser')
        
        # Extract all style tags from head - preserve ALL styles
        style_tags = soup.find_all('style')
        styles_content = ''
        for style_tag in style_tags:
            if style_tag.string:
                style_text = style_tag.string
                # Scope html/body styles to .resume-wrapper .resume-content for higher specificity
                # This ensures template styles override Tailwind and other CSS
                style_text = re.sub(r'html\s*,', '.resume-wrapper .resume-content,', style_text)
                style_text = re.sub(r',\s*html\s*{', ', .resume-wrapper .resume-content {', style_text)
                style_text = re.sub(r'body\s*,', '.resume-wrapper .resume-content,', style_text)
                style_text = re.sub(r',\s*body\s*{', ', .resume-wrapper .resume-content {', style_text)
                # Handle standalone html and body rules - replace with higher specificity
                style_text = re.sub(r'^html\s*{', '.resume-wrapper .resume-content {', style_text, flags=re.MULTILINE)
                style_text = re.sub(r'^body\s*{', '.resume-wrapper .resume-content {', style_text, flags=re.MULTILINE)
                # Convert @page rules - @page doesn't work in regular CSS, so we'll remove it for screen
                # But keep the margin/size info for reference (we handle margins in PDF generation)
                # Remove @page rules entirely for screen preview - they don't apply
                style_text = re.sub(r'@page\s*\{[^}]*\}', '', style_text, flags=re.DOTALL)
                # Scope ALL class selectors to .resume-wrapper .resume-content for maximum specificity
                # This ensures template styles override Tailwind CSS
                def scope_class_selector(match):
                    before = match.group(1)  # Everything before the class selector
                    class_name = match.group(2)  # The class name (e.g., .name, .section-title)
                    after = match.group(3)  # Everything after (usually { or whitespace)
                    
                    # Don't scope if already scoped
                    if '.resume-wrapper .resume-content' in before:
                        return match.group(0)
                    
                    # Don't scope if inside @media print (we handle @page separately)
                    # Check if we're inside a @media block
                    check_text = before[-200:] if len(before) > 200 else before
                    # Count opening and closing braces to see if we're inside @media
                    open_braces = check_text.count('{')
                    close_braces = check_text.count('}')
                    if '@media' in check_text and (open_braces > close_braces):
                        # Inside @media, don't scope - let it apply naturally
                        return match.group(0)
                    
                    # Don't scope if it's part of a compound selector (e.g., ".contact-info .separator")
                    # Check if there's another selector before it on the same line
                    lines = before.split('\n')
                    if lines:
                        last_line = lines[-1].strip()
                        # If last line has a selector pattern before this class, it's compound
                        if re.search(r'[.#\w-]+\s+$', last_line):
                            return match.group(0)
                    
                    return f'{before}.resume-wrapper .resume-content {class_name}{after}'
                
                # Match class selectors that start a new rule (after whitespace, comma, closing brace, or start of line)
                style_text = re.sub(r'([\s,}]*)(\.[a-zA-Z_][a-zA-Z0-9_-]+)(\s*{)', scope_class_selector, style_text, flags=re.MULTILINE)
                
                # Clean up any double-scoping
                style_text = re.sub(r'\.resume-wrapper \.resume-content (\.resume-wrapper \.resume-content )+', '.resume-wrapper .resume-content ', style_text)
                styles_content += style_text + '\n'
        
        # Extract body content - preserve ALL HTML structure exactly
        body_tag = soup.find('body')
        if body_tag and hasattr(body_tag, 'children'):
            # Get all content inside body, preserving all tags and structure
            # Filter out None values that BeautifulSoup might return
            try:
                body_content = ''.join(str(child) for child in body_tag.children if child is not None)
            except (AttributeError, TypeError) as e:
                # Fallback if children iteration fails
                logger.warning(f"Error iterating body children: {e}, using innerHTML fallback")
                body_content = str(body_tag.decode_contents())
        else:
            # Fallback: get all content if no body tag - preserve everything
            body_content = str(soup.decode_contents())
        
        # Ensure we have all content - no truncation
        resume_html = body_content
        context['resume_styles'] = styles_content
        
        # Debug: Log if styles were extracted
        import logging
        logger = logging.getLogger(__name__)
        if styles_content:
            logger.info(f"Extracted {len(styles_content)} characters of styles for template {template_name}")
        else:
            logger.warning(f"No styles extracted for template {template_name}!")
        
    except (ImportError, Exception) as e:
        # Fallback to regex if BeautifulSoup is not available or fails
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"BeautifulSoup not available or failed, using regex fallback: {e}")
        # Fallback to regex if BeautifulSoup is not available
        def extract_body_content(html):
            # Extract ALL styles from head section - preserve all style tags
            style_matches = re.findall(r'<style[^>]*>(.*?)</style>', html, re.DOTALL | re.IGNORECASE)
            all_styles = '\n'.join(style_matches) if style_matches else ''
            
            # Remove DOCTYPE
            html = re.sub(r'<!DOCTYPE[^>]*>', '', html, flags=re.IGNORECASE)
            # Remove html tags
            html = re.sub(r'<html[^>]*>', '', html, flags=re.IGNORECASE)
            html = re.sub(r'</html>', '', html, flags=re.IGNORECASE)
            
            # Scope html/body styles to .resume-wrapper .resume-content for higher specificity
            # Replace html, body selectors with higher specificity to override Tailwind
            all_styles = re.sub(r'html\s*,', '.resume-wrapper .resume-content,', all_styles)
            all_styles = re.sub(r',\s*html\s*{', ', .resume-wrapper .resume-content {', all_styles)
            all_styles = re.sub(r'body\s*,', '.resume-wrapper .resume-content,', all_styles)
            all_styles = re.sub(r',\s*body\s*{', ', .resume-wrapper .resume-content {', all_styles)
            # Handle standalone html and body rules - replace with higher specificity
            all_styles = re.sub(r'^html\s*{', '.resume-wrapper .resume-content {', all_styles, flags=re.MULTILINE)
            all_styles = re.sub(r'^body\s*{', '.resume-wrapper .resume-content {', all_styles, flags=re.MULTILINE)
            # Remove @page rules - they don't work in regular CSS for screen display
            all_styles = re.sub(r'@page\s*\{[^}]*\}', '', all_styles, flags=re.DOTALL)
            # Scope ALL class selectors to .resume-wrapper .resume-content for maximum specificity
            def scope_class_selector_fallback(match):
                before = match.group(1)
                class_name = match.group(2)
                after = match.group(3)
                
                # Don't scope if already scoped
                if '.resume-wrapper .resume-content' in before:
                    return match.group(0)
                
                # Don't scope if inside @media print
                check_text = before[-200:] if len(before) > 200 else before
                open_braces = check_text.count('{')
                close_braces = check_text.count('}')
                if '@media' in check_text and (open_braces > close_braces):
                    return match.group(0)
                
                # Don't scope if part of compound selector
                lines = before.split('\n')
                if lines:
                    last_line = lines[-1].strip()
                    if re.search(r'[.#\w-]+\s+$', last_line):
                        return match.group(0)
                
                return f'{before}.resume-wrapper .resume-content {class_name}{after}'
            
            all_styles = re.sub(r'([\s,}]*)(\.[a-zA-Z_][a-zA-Z0-9_-]+)(\s*{)', scope_class_selector_fallback, all_styles, flags=re.MULTILINE)
            # Clean up any double-scoping
            all_styles = re.sub(r'\.resume-wrapper \.resume-content (\.resume-wrapper \.resume-content )+', '.resume-wrapper .resume-content ', all_styles)
            
            # Remove head section but preserve styles
            html = re.sub(r'<head>.*?</head>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # Remove title tag if present
            html = re.sub(r'<title>.*?</title>', '', html, flags=re.DOTALL | re.IGNORECASE)
            
            # Try to extract body content - preserve ALL content
            body_match = re.search(r'<body[^>]*>(.*)</body>', html, re.DOTALL | re.IGNORECASE)
            if body_match:
                context['resume_styles'] = all_styles
                # Return full body content - no truncation
                return body_match.group(1)
            
            # If no body tag, preserve all remaining HTML content
            # This ensures nothing is lost
            context['resume_styles'] = all_styles
            return html.strip()
        
        resume_html = extract_body_content(resume_html)
    
    context['resume_html'] = resume_html
    
    return render(request, 'resumes/preview_resume.html', context)
