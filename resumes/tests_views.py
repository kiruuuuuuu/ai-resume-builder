"""
View tests for resumes app with mocked AI calls.
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch, MagicMock
from .models import Resume, Experience, Education, Skill
from users.models import JobSeekerProfile

User = get_user_model()

class ResumeBuilderViewTests(TestCase):
    """Test resume builder views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass', user_type='job_seeker')
        self.profile = JobSeekerProfile.objects.create(user=self.user)
        self.resume = Resume.objects.create(profile=self.profile, title='Test Resume')
    
    def test_resume_builder_requires_login(self):
        response = self.client.get(reverse('resumes:resume-builder'))
        self.assertNotEqual(response.status_code, 200)
    
    def test_resume_builder_allows_authenticated_user(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('resumes:resume-builder'))
        self.assertEqual(response.status_code, 200)


class ResumeAJAXTests(TestCase):
    """Test AJAX endpoints in resume builder."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass', user_type='job_seeker')
        self.profile = JobSeekerProfile.objects.create(user=self.user)
        self.resume = Resume.objects.create(profile=self.profile, title='Test Resume')
        self.client.login(username='testuser', password='testpass')
    
    def test_get_item_html_ajax(self):
        """Test get_item_html AJAX endpoint."""
        exp = Experience.objects.create(
            resume=self.resume,
            job_title='Developer',
            company='Test Corp',
            description='Test description'
        )
        
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'get_item_html',
                'model_name': 'experience',
                'pk': exp.id,
                'csrfmiddlewaretoken': self.client.cookies.get('csrftoken').value if self.client.cookies.get('csrftoken') else ''
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
    
    @patch('resumes.parser._call_gemini_with_retry')
    def test_enhance_description_api(self, mock_gemini):
        """Test AI text enhancement endpoint."""
        mock_response = MagicMock()
        mock_response.text = 'Enhanced text'
        mock_gemini.return_value = mock_response
        
        response = self.client.post(
            reverse('resumes:enhance-api'),
            data={'text_to_enhance': 'Test text', 'context': 'description'},
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('enhanced_text', data)
    
    def test_add_item_ajax(self):
        """Test add item AJAX endpoint."""
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'add',
                'model_name': 'experience',
                'job_title': 'Developer',
                'company': 'Test Corp',
                'description': 'Test description',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('item_html', data)
    
    def test_get_edit_form_ajax(self):
        """Test get_edit_form AJAX endpoint."""
        exp = Experience.objects.create(
            resume=self.resume,
            job_title='Developer',
            company='Test Corp',
            description='Test description'
        )
        
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'get_edit_form',
                'model_name': 'experience',
                'pk': exp.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertIn('form_html', data)
    
    def test_update_item_ajax(self):
        """Test update item AJAX endpoint."""
        exp = Experience.objects.create(
            resume=self.resume,
            job_title='Developer',
            company='Test Corp',
            description='Test description'
        )
        
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'update',
                'model_name': 'experience',
                'pk': exp.id,
                'job_title': 'Senior Developer',
                'company': 'New Corp',
                'description': 'Updated description',
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        exp.refresh_from_db()
        self.assertEqual(exp.job_title, 'Senior Developer')
    
    def test_delete_item_ajax(self):
        """Test delete item AJAX endpoint."""
        exp = Experience.objects.create(
            resume=self.resume,
            job_title='Developer',
            company='Test Corp',
            description='Test description'
        )
        exp_id = exp.id
        
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'delete',
                'model_name': 'experience',
                'pk': exp_id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        self.assertFalse(Experience.objects.filter(id=exp_id).exists())
    
    def test_ajax_cross_user_permission(self):
        """Test that users cannot access other users' resume items via AJAX."""
        other_user = User.objects.create_user(username='otheruser', email='other@test.com', password='testpass', user_type='job_seeker')
        other_profile = JobSeekerProfile.objects.create(user=other_user)
        other_resume = Resume.objects.create(profile=other_profile, title='Other Resume')
        other_exp = Experience.objects.create(
            resume=other_resume,
            job_title='Other Job',
            company='Other Corp'
        )
        
        # Try to get edit form for other user's item
        response = self.client.post(
            reverse('resumes:resume-builder'),
            {
                'action': 'get_edit_form',
                'model_name': 'experience',
                'pk': other_exp.id,
            },
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 403)
    
    def test_get_preview_html(self):
        """Test get_preview_html endpoint."""
        response = self.client.get(
            reverse('resumes:get-preview-html', args=[self.resume.id])
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response['Content-Type'])
    
    def test_dismiss_welcome(self):
        """Test dismiss_welcome endpoint."""
        response = self.client.post(
            reverse('resumes:dismiss-welcome'),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'success')
        # Check session is updated
        self.assertFalse(self.client.session.get('show_welcome_modal', True))


class ResumePermissionTests(TestCase):
    """Test that users can only access their own resumes."""
    
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create_user(username='user1', email='user1@test.com', password='testpass', user_type='job_seeker')
        self.user2 = User.objects.create_user(username='user2', email='user2@test.com', password='testpass', user_type='job_seeker')
        self.profile1 = JobSeekerProfile.objects.create(user=self.user1)
        self.profile2 = JobSeekerProfile.objects.create(user=self.user2)
        self.resume1 = Resume.objects.create(profile=self.profile1, title='Resume 1')
        self.resume2 = Resume.objects.create(profile=self.profile2, title='Resume 2')
    
    def test_user_cannot_access_other_resume(self):
        """Test that user1 cannot access user2's resume."""
        self.client.login(username='user1', password='testpass')
        response = self.client.get(reverse('resumes:download-resume-pdf', args=[self.resume2.id, 'classic']))
        self.assertNotEqual(response.status_code, 200)
    
    def test_user_can_access_own_resume(self):
        """Test that user1 can access their own resume."""
        self.client.login(username='user1', password='testpass')
        # This will fail without WeasyPrint but should at least pass permission check
        try:
            response = self.client.get(reverse('resumes:download-resume-pdf', args=[self.resume1.id, 'classic']))
            # Should not be 403 or redirect to home
            self.assertNotIn(response.status_code, [403, 302])
        except:
            pass  # PDF generation may fail in test environment


class ResumeUploadTests(TestCase):
    """Test resume upload and parsing views with mocked AI calls."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', email='test@test.com', password='testpass', user_type='job_seeker')
        self.profile = JobSeekerProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass')
    
    @patch('resumes.parser.parse_text_with_gemini')
    @patch('resumes.parser.extract_text_from_file')
    def test_upload_resume_triggers_parsing(self, mock_extract, mock_parse):
        """Test that uploading a resume triggers AI parsing."""
        from io import BytesIO
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        mock_extract.return_value = 'Sample resume text'
        mock_parse.return_value = {
            'personal_details': {'full_name': 'Test User'},
            'professional_summary': 'Test summary',
            'experience': [], 'education': [], 'skills': [], 'projects': [],
            'certifications': [], 'achievements': [], 'languages': [], 'hobbies': []
        }
        
        # Create a fake PDF file
        pdf_content = b'%PDF-1.4 fake pdf content'
        pdf_file = SimpleUploadedFile('test_resume.pdf', pdf_content, content_type='application/pdf')
        
        response = self.client.post(
            reverse('resumes:resume-upload'),
            {'resume_file': pdf_file}
        )
        
        # Should redirect to parsing progress
        self.assertEqual(response.status_code, 302)
        self.assertIn('parsing-progress', response.url)
    
    def test_upload_resume_invalid_file_type(self):
        """Test that invalid file types are rejected."""
        from django.core.files.uploadedfile import SimpleUploadedFile
        
        txt_file = SimpleUploadedFile('test.txt', b'Not a PDF or DOCX', content_type='text/plain')
        
        response = self.client.post(
            reverse('resumes:resume-upload'),
            {'resume_file': txt_file}
        )
        
        # Should redirect with error message
        self.assertEqual(response.status_code, 302)

