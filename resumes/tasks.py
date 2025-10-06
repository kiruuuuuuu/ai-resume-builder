from celery import shared_task
from django.core.files.storage import FileSystemStorage
from .parser import extract_text_from_docx, extract_text_from_pdf, parse_text_with_gemini, get_full_resume_text, score_and_critique_resume
from .models import Resume, ParsedResumeCache
import json
import logging

# Use a more specific logger for better debugging
logger = logging.getLogger(__name__)

@shared_task
def parse_resume_task(user_id, file_path):
    """
    Asynchronous task to parse a resume file and store the structured data.
    """
    try:
        logger.info(f"Starting resume parse task for user_id: {user_id} and file: {file_path}")
        text = ""
        if file_path.lower().endswith('.pdf'):
            text = extract_text_from_pdf(file_path)
        elif file_path.lower().endswith('.docx'):
            text = extract_text_from_docx(file_path)

        if text:
            logger.info(f"Extracted text from {file_path}. Length: {len(text)} chars. Now calling Gemini for parsing.")
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
            logger.warning(f"No text could be extracted from file {file_path} for user_id: {user_id}.")

        # Clean up the temporary file
        fs = FileSystemStorage()
        if fs.exists(file_path):
            fs.delete(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")

    except Exception as e:
        logger.error(f"Error in parse_resume_task for user {user_id}: {e}", exc_info=True)


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

