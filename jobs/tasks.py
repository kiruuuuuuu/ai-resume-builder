from celery import shared_task
from .models import JobPosting, JobMatchScore
from resumes.models import Resume
from resumes.parser import get_full_resume_text
from .matcher import calculate_match_score

@shared_task
def calculate_and_save_match_score_task(resume_id, job_id):
    """
    Asynchronous task to calculate and save the match score between a resume and a job posting.
    """
    try:
        resume = Resume.objects.get(id=resume_id)
        job = JobPosting.objects.get(id=job_id)

        resume_text = get_full_resume_text(resume)
        job_text = f"{job.title} {job.description} {job.requirements}"
        
        score = calculate_match_score(resume_text, job_text)

        JobMatchScore.objects.update_or_create(
            resume=resume,
            job_posting=job,
            defaults={'score': score}
        )
    except (Resume.DoesNotExist, JobPosting.DoesNotExist):
        print(f"Could not find Resume ({resume_id}) or JobPosting ({job_id}) for scoring.")
    except Exception as e:
        print(f"An error occurred while matching resume {resume_id} and job {job_id}: {e}")
