"""
Tests for job feature blocking decorator.
"""
from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from .models import JobPosting
from users.models import EmployerProfile, JobSeekerProfile

User = get_user_model()


class JobFeatureBlockingTests(TestCase):
    """Test that job features are blocked when JOBS_FEATURE_ENABLED is False."""
    
    def setUp(self):
        self.client = Client()
        self.employer_user = User.objects.create_user(
            username='employer',
            password='testpass',
            user_type='employer'
        )
        self.employer_profile = EmployerProfile.objects.create(user=self.employer_user)
        self.job = JobPosting.objects.create(
            employer=self.employer_profile,
            title='Test Job',
            description='Test',
            requirements='Test',
            location='Test'
        )
        
        self.seeker_user = User.objects.create_user(
            username='seeker',
            password='testpass',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=self.seeker_user)
    
    @override_settings(JOBS_FEATURE_ENABLED=False)
    def test_job_list_redirects_to_coming_soon(self):
        """Test that job list redirects to coming soon when disabled."""
        response = self.client.get(reverse('jobs:job-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Coming Soon')
    
    @override_settings(JOBS_FEATURE_ENABLED=False)
    def test_job_detail_redirects_to_coming_soon(self):
        """Test that job detail redirects to coming soon when disabled."""
        response = self.client.get(reverse('jobs:job-detail', args=[self.job.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Coming Soon')
    
    @override_settings(JOBS_FEATURE_ENABLED=False)
    def test_post_job_redirects_to_coming_soon(self):
        """Test that post job redirects to coming soon when disabled."""
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:post-job'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Coming Soon')
    
    @override_settings(JOBS_FEATURE_ENABLED=False)
    def test_my_applications_redirects_to_coming_soon(self):
        """Test that my applications redirects to coming soon when disabled."""
        self.client.login(username='seeker', password='testpass')
        response = self.client.get(reverse('jobs:my-applications'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Coming Soon')
    
    @override_settings(JOBS_FEATURE_ENABLED=True)
    def test_job_list_works_when_enabled(self):
        """Test that job list works when feature is enabled."""
        response = self.client.get(reverse('jobs:job-list'))
        # Should show job list, not coming soon
        self.assertEqual(response.status_code, 200)
        # Should not contain coming soon message
        self.assertNotContains(response, 'Coming Soon', status_code=200)
    
    @override_settings(JOBS_FEATURE_ENABLED=True)
    def test_post_job_works_when_enabled(self):
        """Test that post job works when feature is enabled."""
        self.client.login(username='employer', password='testpass')
        response = self.client.get(reverse('jobs:post-job'))
        # Should show post job form, not coming soon
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Coming Soon', status_code=200)

