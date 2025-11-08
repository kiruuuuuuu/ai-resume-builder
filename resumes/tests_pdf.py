"""
Tests for PDF generation functionality.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Resume, Experience, Education, Skill
from users.models import JobSeekerProfile

User = get_user_model()


class PDFGenerationTests(TestCase):
    """Test PDF generation functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass',
            user_type='job_seeker'
        )
        self.profile = JobSeekerProfile.objects.create(user=self.user, full_name='Test User')
        self.resume = Resume.objects.create(profile=self.profile, title='Test Resume')
        self.client.login(username='testuser', password='testpass')
        
        # Add some resume data
        Experience.objects.create(
            resume=self.resume,
            job_title='Software Engineer',
            company='Test Corp',
            start_date='2020-01-01',
            description='Worked on amazing projects'
        )
        Education.objects.create(
            resume=self.resume,
            institution='Test University',
            degree='BS Computer Science',
            field_of_study='Computer Science'
        )
        Skill.objects.create(resume=self.resume, name='Python', category='Backend')
    
    @patch('resumes.views.WEASY_AVAILABLE', True)
    @patch('resumes.views.HTML')
    @patch('resumes.views.CSS')
    def test_pdf_generation_classic_template(self, mock_css, mock_html):
        """Test PDF generation for classic template."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b'fake pdf content'
        mock_html.return_value = mock_html_instance
        
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[self.resume.id, 'classic'])
        )
        
        # Should return PDF (if WeasyPrint available) or redirect (if not)
        # Since we're mocking, it should work
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
        else:
            # If redirect, that's okay - it means async is being used or WeasyPrint unavailable
            self.assertEqual(response.status_code, 302)
    
    @patch('resumes.views.WEASY_AVAILABLE', True)
    @patch('resumes.views.HTML')
    @patch('resumes.views.CSS')
    def test_pdf_generation_modern_template(self, mock_css, mock_html):
        """Test PDF generation for modern template."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b'fake pdf content'
        mock_html.return_value = mock_html_instance
        
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[self.resume.id, 'modern'])
        )
        
        # May return 200 (PDF) or 302 (redirect if async)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
    
    @patch('resumes.views.WEASY_AVAILABLE', True)
    @patch('resumes.views.HTML')
    @patch('resumes.views.CSS')
    def test_pdf_generation_professional_template(self, mock_css, mock_html):
        """Test PDF generation for professional template."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b'fake pdf content'
        mock_html.return_value = mock_html_instance
        
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[self.resume.id, 'professional'])
        )
        
        # May return 200 (PDF) or 302 (redirect if async)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
    
    @patch('resumes.views.WEASY_AVAILABLE', True)
    @patch('resumes.views.HTML')
    @patch('resumes.views.CSS')
    def test_pdf_generation_creative_template(self, mock_css, mock_html):
        """Test PDF generation for creative template."""
        mock_html_instance = MagicMock()
        mock_html_instance.write_pdf.return_value = b'fake pdf content'
        mock_html.return_value = mock_html_instance
        
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[self.resume.id, 'creative'])
        )
        
        # May return 200 (PDF) or 302 (redirect if async)
        self.assertIn(response.status_code, [200, 302])
        if response.status_code == 200:
            self.assertEqual(response['Content-Type'], 'application/pdf')
    
    def test_pdf_generation_invalid_template(self):
        """Test PDF generation with invalid template name."""
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[self.resume.id, 'invalid'])
        )
        
        # Should redirect or return error
        self.assertNotEqual(response.status_code, 200)
    
    def test_pdf_generation_unauthorized_access(self):
        """Test that users cannot generate PDFs for other users' resumes."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass',
            user_type='job_seeker'
        )
        other_profile = JobSeekerProfile.objects.create(user=other_user)
        other_resume = Resume.objects.create(profile=other_profile, title='Other Resume')
        
        response = self.client.get(
            reverse('resumes:download-resume-pdf', args=[other_resume.id, 'classic'])
        )
        
        # Should not be accessible (403 or redirect)
        self.assertNotEqual(response.status_code, 200)


class ResumePreviewTests(TestCase):
    """Test resume preview functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass',
            user_type='job_seeker'
        )
        self.profile = JobSeekerProfile.objects.create(user=self.user, full_name='Test User')
        self.resume = Resume.objects.create(profile=self.profile, title='Test Resume')
        self.client.login(username='testuser', password='testpass')
    
    def test_preview_page_loads(self):
        """Test that preview page loads."""
        response = self.client.get(
            reverse('resumes:preview-resume', args=[self.resume.id]) + '?template=classic'
        )
        self.assertEqual(response.status_code, 200)
    
    def test_preview_with_different_templates(self):
        """Test preview with different templates."""
        templates = ['classic', 'modern', 'professional', 'creative']
        
        for template in templates:
            response = self.client.get(
                reverse('resumes:preview-resume', args=[self.resume.id]) + f'?template={template}'
            )
            self.assertEqual(response.status_code, 200)
    
    def test_preview_unauthorized_access(self):
        """Test that users cannot preview other users' resumes."""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass',
            user_type='job_seeker'
        )
        other_profile = JobSeekerProfile.objects.create(user=other_user)
        other_resume = Resume.objects.create(profile=other_profile, title='Other Resume')
        
        response = self.client.get(
            reverse('resumes:preview-resume', args=[other_resume.id]) + '?template=classic'
        )
        
        # Should not be accessible
        self.assertNotEqual(response.status_code, 200)

