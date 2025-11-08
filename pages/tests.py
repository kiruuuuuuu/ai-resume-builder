from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import BugReport
from users.models import JobSeekerProfile, EmployerProfile
from jobs.models import JobPosting

User = get_user_model()


class HomeViewTests(TestCase):
    """Test home view functionality."""
    
    def setUp(self):
        self.client = Client()
    
    def test_home_page_loads_for_anonymous_user(self):
        """Test that home page loads for anonymous users."""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Resume Builder')
    
    def test_home_page_loads_for_job_seeker(self):
        """Test that home page loads for job seekers."""
        user = User.objects.create_user(
            username='seeker',
            password='testpass123',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=user)
        self.client.login(username='seeker', password='testpass123')
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_loads_for_employer(self):
        """Test that home page loads for employers."""
        user = User.objects.create_user(
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        EmployerProfile.objects.create(user=user)
        self.client.login(username='employer', password='testpass123')
        
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
    
    def test_home_page_redirects_employer_to_onboarding(self):
        """Test that employers without company details are redirected to onboarding."""
        user = User.objects.create_user(
            username='employer',
            password='testpass123',
            user_type='employer'
        )
        # Create profile without company details
        EmployerProfile.objects.create(user=user, company_name='', company_website='')
        self.client.login(username='employer', password='testpass123')
        
        response = self.client.get(reverse('home'))
        # Should redirect to onboarding
        self.assertEqual(response.status_code, 302)
        self.assertIn('employer-onboarding', response.url)


class BugReportTests(TestCase):
    """Test bug report functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=self.user)
    
    def test_bug_report_creates_bug(self):
        """Test that bug report creates a BugReport object."""
        self.client.login(username='testuser', password='testpass123')
        
        import json
        response = self.client.post(
            reverse('report-bug'),
            data=json.dumps({
                'description': 'Test bug description with enough characters to pass validation',
                'url': 'http://test.com/page',
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        
        # Verify bug was created
        self.assertTrue(BugReport.objects.filter(description='Test bug description with enough characters to pass validation').exists())
    
    def test_bug_report_with_screenshot(self):
        """Test bug report with screenshot upload."""
        self.client.login(username='testuser', password='testpass123')
        
        import json
        import base64
        
        # Create a fake base64 encoded image
        fake_image_data = base64.b64encode(b'fake image content').decode('utf-8')
        
        response = self.client.post(
            reverse('report-bug'),
            data=json.dumps({
                'description': 'Test bug with screenshot and enough characters',
                'url': 'http://test.com/page',
                'screenshot': f'data:image/png;base64,{fake_image_data}',
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return success
        self.assertEqual(response.status_code, 200)
        
        # Verify bug was created
        bug = BugReport.objects.filter(description='Test bug with screenshot and enough characters').first()
        self.assertIsNotNone(bug)
    
    def test_bug_report_anonymous_user(self):
        """Test that anonymous users can also report bugs."""
        import json
        response = self.client.post(
            reverse('report-bug'),
            data=json.dumps({
                'description': 'Anonymous bug report with enough characters to pass validation',
                'url': 'http://test.com/page',
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should still work (bug reports can be anonymous)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertTrue(BugReport.objects.filter(description='Anonymous bug report with enough characters to pass validation').exists())
    
    def test_bug_report_requires_description(self):
        """Test that bug report requires description."""
        self.client.login(username='testuser', password='testpass123')
        
        import json
        response = self.client.post(
            reverse('report-bug'),
            data=json.dumps({
                'url': 'http://test.com/page',
                # Missing description
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
    
    def test_bug_report_description_too_short(self):
        """Test that bug report requires description with at least 10 characters."""
        self.client.login(username='testuser', password='testpass123')
        
        import json
        response = self.client.post(
            reverse('report-bug'),
            data=json.dumps({
                'description': 'Short',
                'url': 'http://test.com/page',
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return error
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertEqual(data['status'], 'error')
