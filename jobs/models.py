from django.db import models
from users.models import CustomUser, JobSeekerProfile, EmployerProfile
from django.utils import timezone
from resumes.models import Resume

class JobPosting(models.Model):
    """
    Represents a job posting created by an Employer.
    """
    employer = models.ForeignKey(EmployerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField()
    location = models.CharField(max_length=255)
    salary_range = models.CharField(max_length=100, null=True, blank=True)  # Deprecated, use salary_min/salary_max
    salary_min = models.IntegerField(null=True, blank=True, help_text="Minimum salary in USD")
    salary_max = models.IntegerField(null=True, blank=True, help_text="Maximum salary in USD")
    vacancies = models.PositiveIntegerField(default=1, help_text="Number of available positions for this role.")
    application_deadline = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # This field tracks the last update

    def __str__(self):
        return self.title

    @property
    def is_active(self):
        """
        Checks if the application deadline has passed.
        """
        if self.application_deadline:
            return timezone.now() < self.application_deadline
        return True

class Application(models.Model):
    """
    Represents a job application submitted by a Job Seeker for a Job Posting.
    """
    TEMPLATE_CHOICES = [
        ('classic', 'Classic'),
        ('modern', 'Modern'),
        ('professional', 'Professional'),
    ]
    STATUS_CHOICES = [
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Shortlisted', 'Shortlisted'),
        ('Interview', 'Interview'),
        ('Offered', 'Offered'),
        ('Rejected', 'Rejected'),
    ]
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    applicant = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    applied_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Submitted')
    resume_template = models.CharField(max_length=20, choices=TEMPLATE_CHOICES, default='classic')


    def __str__(self):
        return f"{self.applicant.user.username}'s application for {self.job_posting.title}"

class Notification(models.Model):
    """
    A notification for users, typically for employers about new applications.
    """
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.CharField(max_length=255)
    link = models.URLField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message

class Interview(models.Model):
    """
    Represents an interview scheduled for a specific job application.
    """
    INTERVIEW_STATUS_CHOICES = [
        ('Proposed', 'Proposed'),
        ('Scheduled', 'Scheduled'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    ]
    application = models.OneToOneField(Application, on_delete=models.CASCADE)
    confirmed_slot = models.DateTimeField(null=True, blank=True)
    interview_details = models.TextField(null=True, blank=True) # e.g., Meet link, address
    status = models.CharField(max_length=20, choices=INTERVIEW_STATUS_CHOICES, default='Proposed')

    def __str__(self):
        return f"Interview for {self.application}"

class InterviewSlot(models.Model):
    """
    Represents a proposed time slot for an interview. An interview can have multiple slots.
    """
    interview = models.ForeignKey(Interview, related_name='slots', on_delete=models.CASCADE)
    proposed_time = models.DateTimeField()

    def __str__(self):
        return f"Slot for {self.interview.application} at {self.proposed_time}"

class JobMatchScore(models.Model):
    """
    Stores the calculated match score between a specific resume and job posting
    to act as a cache and improve performance.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_posting = models.ForeignKey(JobPosting, on_delete=models.CASCADE)
    score = models.IntegerField()
    last_calculated = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('resume', 'job_posting')

    def __str__(self):
        return f"{self.score}% match for {self.resume.profile.user.username} on {self.job_posting.title}"

