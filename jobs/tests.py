from django.test import TestCase, Client
from .forms import JobPostingForm
from django.utils import timezone
import datetime
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import JobPosting
from users.models import EmployerProfile, JobSeekerProfile

class JobFormTests(TestCase):
    """Tests for the forms in the jobs app."""

    def test_job_posting_form_valid_data(self):
        """Test that the JobPostingForm is valid with correct data."""
        form_data = {
            'title': 'Senior Software Engineer',
            'description': 'We are looking for an experienced Senior Software Engineer to join our dynamic team and build amazing things.',
            'requirements': '5+ years of professional experience in Python, Django, and cloud services like AWS or GCP.',
            'location': 'Remote',
            'application_deadline': timezone.now() + datetime.timedelta(days=30)
        }
        form = JobPostingForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_job_posting_form_deadline_in_past(self):
        """Test that the form is invalid if the application deadline is in the past."""
        form_data = {
            'title': 'Time Traveler Position',
            'description': 'Must have a time machine and be able to work in the past, present, and future simultaneously.',
            'requirements': 'Ability to bend spacetime and fix bugs before they are written.',
            'location': 'Anywhen',
            'application_deadline': timezone.now() - datetime.timedelta(days=1)
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('application_deadline', form.errors)
        self.assertEqual(form.errors['application_deadline'][0], 'Application deadline cannot be in the past.')

    def test_job_posting_form_invalid_salary(self):
        """Test that the form is invalid if the salary range contains no numbers."""
        form_data = {
            'title': 'Great Job with Great Pay',
            'description': 'A really great job where you will be doing great things and making a great impact on the world.',
            'requirements': 'Must be great and have a great attitude. A great personality is a plus. Greatness is required.',
            'location': 'Here',
            'salary_range': 'A lot of money'
        }
        form = JobPostingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('salary_range', form.errors)
        self.assertEqual(form.errors['salary_range'][0], 'Salary range must contain a number.')

class JobViewTests(TestCase):
    """Tests for the views in the jobs app."""

    def setUp(self):
        """Set up users, profiles, and a job posting for view tests."""
        User = get_user_model()
        self.employer_user = User.objects.create_user(username='testemployer', password='testpassword', user_type='employer')
        self.seeker_user = User.objects.create_user(username='testseeker', password='testpassword', user_type='job_seeker')

        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user)
        self.seeker_profile = JobSeekerProfile.objects.create(user=self.seeker_user)

        self.job_posting = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test Description',
            requirements='Test Requirements',
            location='Test Location'
        )

    def test_job_list_view_loads_for_anonymous_user(self):
        """Test that the job list view loads correctly for an anonymous user."""
        url = reverse('jobs:job-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Job')

