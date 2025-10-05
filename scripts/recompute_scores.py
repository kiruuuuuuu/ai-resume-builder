import os
import django
import sys

# Configure Django settings for standalone script
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# Optionally ensure the project root is on sys.path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

django.setup()

from jobs.models import JobMatchScore
from resumes.parser import get_full_resume_text
from jobs.matcher import calculate_match_score


def main():
    all_scores = JobMatchScore.objects.all()
    if not all_scores.exists():
        print('No JobMatchScore rows to recompute.')
        return

    for jms in all_scores:
        resume = jms.resume
        job = jms.job_posting
        resume_text = get_full_resume_text(resume)
        job_text = f"{job.title} {job.description} {job.requirements}"
        new_score = calculate_match_score(resume_text, job_text)
        print(f"Recomputing id={jms.id}: old={jms.score} -> new={new_score}")
        jms.score = new_score
        jms.save()

if __name__ == '__main__':
    main()
