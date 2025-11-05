"""
View tests for jobs app with mocked AI calls.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import JobPosting, Application, Interview, InterviewSlot
from users.models import EmployerProfile, JobSeekerProfile
from resumes.models import Resume

User = get_user_model()

class JobListViewTests(TestCase):
    """Test job list view with filtering."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Python Developer',
            description='Test description',
            requirements='Python, Django',
            location='Remote',
            salary_min=80000,
            salary_max=120000
        )
    
    def test_job_list_view_unauthenticated(self):
        response = self.client.get(reverse('jobs:job-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Developer')
    
    def test_job_list_search_filter(self):
        response = self.client.get(reverse('jobs:job-list') + '?search=Python')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Developer')
    
    def test_job_list_location_filter(self):
        response = self.client.get(reverse('jobs:job-list') + '?location=Remote')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Python Developer')
    
    def test_job_list_salary_filter(self):
        response = self.client.get(reverse('jobs:job-list') + '?salary_min=70000&salary_max=100000')
        self.assertEqual(response.status_code, 200)


class JobPostingViewTests(TestCase):
    """Test job posting views with permission checks."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.seeker_user = User.objects.create_user(username='seeker', email='seeker@test.com', password='testpass', user_type='job_seeker')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
    
    def test_post_job_view_requires_employer(self):
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:post-job'))
        self.assertNotEqual(response.status_code, 200)  # Should redirect or 403
    
    def test_post_job_view_allows_employer(self):
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:post-job'))
        self.assertEqual(response.status_code, 200)


class AIAPITests(TestCase):
    """Test AI API endpoints with mocked Gemini calls."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.seeker_user = User.objects.create_user(username='seeker', email='seeker@test.com', password='testpass', user_type='job_seeker')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
        self.seeker_profile = JobSeekerProfile.objects.create(user=self.seeker_user)
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
    
    @patch('jobs.matcher._call_gemini_with_retry')
    def test_generate_job_description_api(self, mock_gemini):
        """Test AI job description generation endpoint."""
        mock_response = MagicMock()
        mock_response.text = '{"description": "Test description", "requirements": "Test requirements"}'
        mock_gemini.return_value = mock_response
        
        self.client.login(username='employer', password='testpass')
        response = self.client.post(
            reverse('jobs:generate-job-description'),
            data={'title': 'Python Developer', 'keywords': 'Django, AWS'},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    @patch('jobs.matcher._call_gemini_with_retry')
    def test_generate_applicant_summary_api(self, mock_gemini):
        """Test AI applicant summary endpoint."""
        resume = Resume.objects.create(profile=self.seeker_profile, title='Test Resume')
        application = Application.objects.create(
            job_posting=self.job,
            applicant=self.seeker_profile
        )
        
        mock_response = MagicMock()
        mock_response.text = '{"summary": "- Point 1\\n- Point 2\\n- Point 3"}'
        mock_gemini.return_value = mock_response
        
        self.client.login(username='employer', password='testpass')
        response = self.client.post(
            reverse('jobs:generate-applicant-summary'),
            data={'application_id': application.id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    @patch('jobs.matcher._call_gemini_with_retry')
    def test_generate_interview_prep_api(self, mock_gemini):
        """Test AI interview preparation endpoint."""
        resume = Resume.objects.create(profile=self.seeker_profile, title='Test Resume')
        application = Application.objects.create(
            job_posting=self.job,
            applicant=self.seeker_profile,
            status='Interview'
        )
        
        mock_response = MagicMock()
        mock_response.text = '{"questions": [{"question": "Q1", "answer": "A1"}, {"question": "Q2", "answer": "A2"}]}'
        mock_gemini.return_value = mock_response
        
        self.client.login(username='seeker', password='testpass')
        response = self.client.post(
            reverse('jobs:generate-interview-prep'),
            data={'application_id': application.id},
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')


class AJAXEndpointTests(TestCase):
    """Test AJAX endpoints with proper headers."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
    
    def test_generate_job_description_with_ajax_header(self):
        """Test that AJAX endpoint responds correctly with X-Requested-With header."""
        self.client.login(username='employer', password='testpass')
        response = self.client.post(
            reverse('jobs:generate-job-description'),
            data={'title': 'Test'},
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        # Should not be a redirect
        self.assertIn(response.status_code, [200, 400, 500])


class PermissionTests(TestCase):
    """Test role-based access control."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.seeker_user = User.objects.create_user(username='seeker', email='seeker@test.com', password='testpass', user_type='job_seeker')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
    
    def test_job_seeker_cannot_access_employer_views(self):
        """Test that job seekers get 403 or redirect from employer-only views."""
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:post-job'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_employer_cannot_access_job_seeker_views(self):
        """Test that employers get 403 or redirect from job seeker-only views."""
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:my-applications'))
        self.assertNotEqual(response.status_code, 200)


class ApplicationViewTests(TestCase):
    """Test application-related views."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.seeker_user = User.objects.create_user(username='seeker', email='seeker@test.com', password='testpass', user_type='job_seeker')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
        self.seeker_profile = JobSeekerProfile.objects.create(user=self.seeker_user)
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
        self.resume = Resume.objects.create(profile=self.seeker_profile, title='Test Resume')
        self.application = Application.objects.create(
            job_posting=self.job,
            applicant=self.seeker_profile
        )
    
    def test_my_applications_view_requires_login(self):
        """Test that my_applications requires authentication."""
        response = self.client.get(reverse('jobs:my-applications'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_my_applications_view_allows_seeker(self):
        """Test that job seekers can access my_applications."""
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:my-applications'))
        self.assertEqual(response.status_code, 200)
    
    def test_view_applicants_view_requires_employer(self):
        """Test that view_applicants requires employer role."""
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:view-applicants', args=[self.job.id]))
        self.assertNotEqual(response.status_code, 200)
    
    def test_view_applicants_view_allows_employer(self):
        """Test that employers can view applicants."""
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:view-applicants', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_view_applicants_only_shows_own_job(self):
        """Test that employers can only view applicants for their own jobs."""
        other_employer = User.objects.create_user(username='other', email='other@test.com', password='testpass', user_type='employer')
        other_profile = EmployerProfile.objects.create(user=other_employer, company_name='Other Corp')
        other_job = JobPosting.objects.create(
            employer=other_profile,
            title='Other Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
        
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:view-applicants', args=[other_job.id]))
        # Should not be accessible (403 or redirect)
        self.assertNotEqual(response.status_code, 200)


class CompanyProfileViewTests(TestCase):
    """Test company profile views."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.employer_profile = EmployerProfile.objects.create(
            user=self.employer_user,
            company_name='Test Corp',
            company_bio='A great company',
            location='Remote',
            industry='Technology'
        )
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
    
    def test_company_profile_view_public(self):
        """Test that company profile is publicly accessible."""
        response = self.client.get(reverse('jobs:company-profile', args=[self.employer_profile.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Corp')
    
    def test_company_profile_shows_active_jobs(self):
        """Test that company profile shows active jobs."""
        response = self.client.get(reverse('jobs:company-profile', args=[self.employer_profile.user.id]))
        self.assertContains(response, 'Test Job')


class JobStatsViewTests(TestCase):
    """Test job statistics views."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(username='employer', email='employer@test.com', password='testpass', user_type='employer')
        self.seeker_user = User.objects.create_user(username='seeker', email='seeker@test.com', password='testpass', user_type='job_seeker')
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user, company_name='Test Corp')
        self.seeker_profile = JobSeekerProfile.objects.create(user=self.seeker_user)
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
        self.application = Application.objects.create(
            job_posting=self.job,
            applicant=self.seeker_profile,
            status='Submitted'
        )
    
    def test_job_stats_requires_employer(self):
        """Test that job stats requires employer role."""
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:job-stats', args=[self.job.id]))
        self.assertNotEqual(response.status_code, 200)
    
    def test_job_stats_allows_employer(self):
        """Test that employers can view job stats."""
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:job-stats', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
    
    def test_job_stats_only_shows_own_job(self):
        """Test that employers can only view stats for their own jobs."""
        other_employer = User.objects.create_user(username='other', email='other@test.com', password='testpass', user_type='employer')
        other_profile = EmployerProfile.objects.create(user=other_employer, company_name='Other Corp')
        other_job = JobPosting.objects.create(
            employer=other_profile,
            title='Other Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
        
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:job-stats', args=[other_job.id]))
        # Should not be accessible (403 or redirect)
        self.assertNotEqual(response.status_code, 200)

