from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """
    Custom user model to differentiate between Job Seekers and Employers.
    """
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='job_seeker')

class JobSeekerProfile(models.Model):
    """
    Profile for users who are seeking jobs.
    Linked one-to-one with the CustomUser model.
    """
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    full_name = models.CharField(max_length=255, null=True, blank=True)
    professional_summary = models.TextField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    # CORRECT: The email field was correctly removed from here, as it belongs to the CustomUser model.
    address = models.CharField(max_length=255, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    portfolio_url = models.URLField(null=True, blank=True)
    linkedin_url = models.URLField(null=True, blank=True) # New Field

    def __str__(self):
        return self.user.username

class EmployerProfile(models.Model):
    """
    Profile for users who are employers/recruiters.
    Linked one-to-one with the CustomUser model.
    """
    INDUSTRY_CHOICES = [
        ('Technology', 'Technology'),
        ('Finance', 'Finance'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Retail', 'Retail'),
        ('Manufacturing', 'Manufacturing'),
        ('Consulting', 'Consulting'),
        ('Other', 'Other'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, primary_key=True)
    company_name = models.CharField(max_length=255, null=True, blank=True)
    company_website = models.URLField(null=True, blank=True)
    company_description = models.TextField(null=True, blank=True)
    company_logo = models.ImageField(upload_to='company_logos/', null=True, blank=True)
    company_bio = models.TextField(null=True, blank=True, help_text="Extended company biography for public profile")
    location = models.CharField(max_length=255, null=True, blank=True)
    industry = models.CharField(max_length=50, choices=INDUSTRY_CHOICES, null=True, blank=True)

    def __str__(self):
        return self.company_name or self.user.username

