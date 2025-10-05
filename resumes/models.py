from django.db import models
from users.models import JobSeekerProfile

class ParsedResumeCache(models.Model):
    profile = models.OneToOneField(JobSeekerProfile, on_delete=models.CASCADE, primary_key=True)
    parsed_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

class Resume(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) # This field tracks the last update
    # New fields for storing AI score and feedback
    score = models.IntegerField(null=True, blank=True)
    feedback = models.JSONField(null=True, blank=True)


    def __str__(self):
        return self.title

class Experience(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.job_title} at {self.company}"

class Education(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    institution = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255, null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    percentage = models.CharField(max_length=10, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)


    def __str__(self):
        return f"{self.degree} from {self.institution}"

class Skill(models.Model):
    SKILL_CATEGORY_CHOICES = [
        ('Frontend', 'Frontend'),
        ('Backend', 'Backend'),
        ('Database', 'Database'),
        ('DevOps', 'DevOps'),
        ('Tools', 'Tools'),
        ('Other', 'Other'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100, choices=SKILL_CATEGORY_CHOICES, default='Other')


    def __str__(self):
        return self.name

class Project(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    aim = models.TextField(blank=True, null=True, help_text="A brief, 2-line aim of the project.")
    frontend = models.CharField(max_length=255, blank=True, null=True)
    backend = models.CharField(max_length=255, blank=True, null=True)
    database = models.CharField(max_length=255, blank=True, null=True)
    link = models.URLField(null=True, blank=True)


    def __str__(self):
        return self.title

class Certification(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    issuing_organization = models.CharField(max_length=255, blank=True, null=True)
    date_issued = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.name

class Achievement(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()

    def __str__(self):
        return self.name or self.description[:50]
    
class Language(models.Model):
    PROFICIENCY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
        ('Fluent', 'Fluent'),
        ('Native', 'Native'),
    ]
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    proficiency = models.CharField(
        max_length=100,
        choices=PROFICIENCY_CHOICES,
        default='Intermediate',
        blank=True, 
        null=True
    )

    def __str__(self):
        return self.name

class Hobby(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


