from celery import shared_task
from django.core.files.storage import FileSystemStorage, default_storage
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.conf import settings
from django.utils import timezone
from .parser import extract_text_from_docx, extract_text_from_pdf, parse_text_with_gemini, get_full_resume_text, score_and_critique_resume
from .models import Resume, ParsedResumeCache, ResumePDFGeneration, Experience, Education, Skill, Project, Certification, Achievement, Language, Hobby
import json
import logging
import os
import base64
import tempfile

# Use a more specific logger for better debugging
logger = logging.getLogger(__name__)

@shared_task
def parse_resume_task(user_id, filename, file_content_b64):
    """
    Asynchronous task to parse a resume file and store the structured data.
    
    Args:
        user_id: The ID of the user uploading the resume
        filename: The original filename (e.g., 'resume.pdf')
        file_content_b64: Base64-encoded file content as a string
    """
    temp_file_path = None
    try:
        logger.info(f"Starting resume parse task for user_id: {user_id} and file: {filename}")
        
        # Decode base64 file content
        file_content = base64.b64decode(file_content_b64)
        
        # Create a temporary file to store the content
        # This is necessary because PyMuPDF and python-docx require file paths
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
        
        logger.info(f"Created temporary file: {temp_file_path} for processing")
        
        # Extract text from the file
        text = ""
        if filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(temp_file_path)
        elif filename.lower().endswith('.docx'):
            text = extract_text_from_docx(temp_file_path)
        else:
            logger.error(f"Unsupported file type: {filename}")

        if text:
            logger.info(f"Extracted text from {filename}. Length: {len(text)} chars. Now calling Gemini for parsing.")
            structured_data = parse_text_with_gemini(text)
            if structured_data:
                logger.info(f"Successfully parsed resume data for user_id: {user_id}.")
                # Use update_or_create to handle existing entries
                ParsedResumeCache.objects.update_or_create(
                    profile_id=user_id,
                    defaults={'parsed_data': structured_data}
                )
            else:
                logger.error(f"Gemini parsing returned no structured data for user_id: {user_id}.")
        else:
            logger.warning(f"No text could be extracted from file {filename} for user_id: {user_id}.")

    except Exception as e:
        logger.error(f"Error in parse_resume_task for user {user_id}: {e}", exc_info=True)
    finally:
        # Clean up the temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
                logger.info(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")


@shared_task
def update_resume_score_task(resume_id):
    """
    Asynchronous task to calculate and save the AI score and feedback for a resume.
    """
    logger.info(f"Starting score update for Resume ID: {resume_id}")
    try:
        resume = Resume.objects.get(id=resume_id)
        full_resume_text = get_full_resume_text(resume)

        if not full_resume_text.strip() or len(full_resume_text.strip()) < 100:
             logger.warning(f"Resume {resume_id} has insufficient content to score. Setting score to 0.")
             resume.score = 0
             resume.feedback = json.dumps(["Resume is too empty to provide a score. Please add more content."])
             resume.save()
             return

        logger.info(f"Resume {resume_id} has sufficient content. Calling Gemini for scoring and critique.")
        score_data = score_and_critique_resume(full_resume_text)

        if score_data and 'score' in score_data and 'feedback' in score_data:
            resume.score = score_data.get('score')
            resume.feedback = json.dumps(score_data.get('feedback', []))
            resume.save()
            logger.info(f"Successfully updated score for Resume ID: {resume_id} to {resume.score}")
        else:
            logger.error(f"Failed to get valid score_data from AI for Resume ID: {resume_id}. AI response was: {score_data}")

    except Resume.DoesNotExist:
        logger.error(f"Resume with ID {resume_id} not found for scoring.")
    except Exception as e:
        logger.error(f"An unexpected error occurred in update_resume_score_task for resume {resume_id}: {e}", exc_info=True)

@shared_task
def generate_resume_pdf_task(pdf_generation_id, base_url):
    """
    Asynchronous task to generate a PDF resume.
    Updates the ResumePDFGeneration model with status and file.
    """
    logger.info(f"Starting PDF generation task for PDF Generation ID: {pdf_generation_id}")
    
    try:
        pdf_gen = ResumePDFGeneration.objects.get(id=pdf_generation_id)
        pdf_gen.status = 'processing'
        pdf_gen.save(update_fields=['status'])
        
        resume = pdf_gen.resume
        
        # Check if WeasyPrint is available
        try:
            from weasyprint import HTML, CSS
        except ImportError:
            pdf_gen.status = 'failed'
            pdf_gen.error_message = 'PDF generation service (WeasyPrint) is not available.'
            pdf_gen.save(update_fields=['status', 'error_message'])
            logger.error("WeasyPrint is not available for PDF generation.")
            return
        
        # Get resume context
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

        # Group skills by category
        skills_by_category = {}
        skills_qs = Skill.objects.filter(resume=resume).order_by('category')
        for skill in skills_qs:
            category = skill.get_category_display()
            if category not in skills_by_category:
                skills_by_category[category] = []
            skills_by_category[category].append(skill.name)

        # Color mapping
        color_map = {
            'blue': '#3498db',
            'teal': '#14b8a6',
            'indigo': '#6366f1',
            'purple': '#a855f7',
            'red': '#ef4444',
            'graphite': '#475569',
        }
        accent_color_hex = color_map.get(pdf_gen.accent_color, '#3498db')

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
            'accent_color': accent_color_hex,
        }
        
        # Render template
        template_path = f'resumes/resume_pdf_{pdf_gen.template_name}.html'
        template = get_template(template_path)
        html = template.render(context)
        
        # Generate PDF with template-specific margins
        html_obj = HTML(string=html, base_url=base_url)
        # Set template-specific margins to match the template's @page rules
        if pdf_gen.template_name == 'modern':
            page_css = '@page { size: A4; margin: 0 }'
        elif pdf_gen.template_name == 'creative':
            page_css = '@page { size: A4; margin: 0.5cm }'
        else:  # classic and professional
            page_css = '@page { size: A4; margin: 1.5cm }'
        pdf_bytes = html_obj.write_pdf(stylesheets=[CSS(string=page_css)])
        
        # Save PDF file
        filename = f"resume_{resume.id}_{pdf_gen.template_name}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        pdf_gen.pdf_file.save(filename, ContentFile(pdf_bytes), save=False)
        pdf_gen.status = 'completed'
        pdf_gen.completed_at = timezone.now()
        pdf_gen.save(update_fields=['status', 'pdf_file', 'completed_at'])
        
        logger.info(f"Successfully generated PDF for Resume ID: {resume.id}, PDF Generation ID: {pdf_generation_id}")
        
    except ResumePDFGeneration.DoesNotExist:
        logger.error(f"PDF Generation with ID {pdf_generation_id} not found.")
    except Exception as e:
        logger.error(f"Error generating PDF for PDF Generation ID {pdf_generation_id}: {e}", exc_info=True)
        try:
            pdf_gen = ResumePDFGeneration.objects.get(id=pdf_generation_id)
            pdf_gen.status = 'failed'
            pdf_gen.error_message = str(e)
            pdf_gen.save(update_fields=['status', 'error_message'])
        except:
            pass

