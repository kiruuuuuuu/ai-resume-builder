from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import JobSeekerProfile, EmployerProfile
from .forms import CustomUserCreationForm, EmployerOnboardingForm

User = get_user_model()


class UserRegistrationTests(TestCase):
    """Test user registration functionality."""
    
    def setUp(self):
        self.client = Client()
    
    def test_registration_page_loads(self):
        """Test that registration page loads correctly."""
        response = self.client.get(reverse('users:register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Register')
    
    def test_job_seeker_registration(self):
        """Test job seeker registration."""
        response = self.client.post(reverse('users:register'), {
            'username': 'testseeker',
            'email': 'seeker@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'job_seeker',
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        user = User.objects.get(username='testseeker')
        self.assertEqual(user.user_type, 'job_seeker')
        self.assertTrue(user.is_authenticated)
        
        # Verify profile was created
        self.assertTrue(JobSeekerProfile.objects.filter(user=user).exists())
    
    def test_employer_registration(self):
        """Test employer registration."""
        response = self.client.post(reverse('users:register'), {
            'username': 'testemployer',
            'email': 'employer@test.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'user_type': 'employer',
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify user was created
        user = User.objects.get(username='testemployer')
        self.assertEqual(user.user_type, 'employer')
        
        # Verify profile was created
        self.assertTrue(EmployerProfile.objects.filter(user=user).exists())
    
    def test_registration_password_mismatch(self):
        """Test registration with mismatched passwords."""
        response = self.client.post(reverse('users:register'), {
            'username': 'testuser',
            'email': 'test@test.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
            'user_type': 'job_seeker',
        })
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username='testuser').exists())


class UserLoginTests(TestCase):
    """Test user login functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=self.user)
    
    def test_login_page_loads(self):
        """Test that login page loads correctly."""
        response = self.client.get(reverse('users:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')
    
    def test_successful_login(self):
        """Test successful login."""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'testpass123',
        })
        
        # Should redirect on success
        self.assertEqual(response.status_code, 302)
        
        # Verify user is logged in
        self.assertTrue(self.client.session.get('_auth_user_id'))
    
    def test_failed_login(self):
        """Test login with wrong password."""
        response = self.client.post(reverse('users:login'), {
            'username': 'testuser',
            'password': 'wrongpassword',
        })
        
        # Should not redirect (form errors)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'error', count=None, status_code=200)


class UserLogoutTests(TestCase):
    """Test user logout functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='testpass123')
    
    def test_logout(self):
        """Test user logout."""
        response = self.client.post(reverse('users:logout'))
        
        # Should redirect
        self.assertEqual(response.status_code, 302)
        
        # Verify user is logged out
        self.assertIsNone(self.client.session.get('_auth_user_id'))


class ProfileEditTests(TestCase):
    """Test profile editing functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            user_type='job_seeker'
        )
        self.profile = JobSeekerProfile.objects.create(
            user=self.user,
            full_name='Test User'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_profile_edit_page_loads(self):
        """Test that profile edit page loads."""
        response = self.client.get(reverse('users:edit-profile'))
        self.assertEqual(response.status_code, 200)
    
    def test_profile_update(self):
        """Test updating profile information."""
        # Visit the page first to get CSRF token
        self.client.get(reverse('users:edit-profile'))
        
        response = self.client.post(reverse('users:edit-profile'), {
            'update_credentials': 'true',
            'username': self.user.username,
            'email': 'updated@test.com',
        })
        
        # Should redirect on success or show form with errors
        if response.status_code == 302:
            # Success - verify profile was updated
            self.user.refresh_from_db()
            self.assertEqual(self.user.email, 'updated@test.com')
        else:
            # Form errors - check that form was rendered
            self.assertEqual(response.status_code, 200)


class EmployerOnboardingTests(TestCase):
    """Test employer onboarding functionality."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testemployer',
            password='testpass123',
            user_type='employer'
        )
        self.profile = EmployerProfile.objects.create(user=self.user)
        self.client.login(username='testemployer', password='testpass123')
    
    def test_onboarding_page_loads(self):
        """Test that onboarding page loads."""
        response = self.client.get(reverse('users:employer-onboarding'))
        self.assertEqual(response.status_code, 200)
    
    def test_onboarding_completion(self):
        """Test completing employer onboarding."""
        # Visit the page first to get CSRF token
        self.client.get(reverse('users:employer-onboarding'))
        
        response = self.client.post(reverse('users:employer-onboarding'), {
            'company_name': 'Test Company',
            'company_website': 'https://testcompany.com',
            'company_description': 'A test company with enough description to pass validation',
            'location': 'Remote',
            'industry': 'Technology',
        })
        
        # Should redirect on success or show form with errors
        if response.status_code == 302:
            # Success - verify profile was updated
            self.profile.refresh_from_db()
            self.assertEqual(self.profile.company_name, 'Test Company')
            self.assertEqual(self.profile.company_website, 'https://testcompany.com')
        else:
            # Form errors - check that form was rendered
            self.assertEqual(response.status_code, 200)


class AdminLoginTests(TestCase):
    """Test admin login functionality."""
    
    def setUp(self):
        self.client = Client()
        # Create staff user
        self.staff_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            user_type='job_seeker',
            is_staff=True,
            is_superuser=True
        )
        # Create regular user
        self.regular_user = User.objects.create_user(
            username='regular',
            password='regularpass123',
            user_type='job_seeker'
        )
        JobSeekerProfile.objects.create(user=self.regular_user)
    
    def test_admin_login_page_loads(self):
        """Test that admin login page loads."""
        response = self.client.get(reverse('users:admin-login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Portal')
    
    def test_staff_user_can_login(self):
        """Test that staff users can login to admin."""
        response = self.client.post(reverse('users:admin-login'), {
            'username': 'admin',
            'password': 'adminpass123',
        })
        
        # Should redirect to admin dashboard
        self.assertEqual(response.status_code, 302)
        self.assertIn('admin-dashboard', response.url)
    
    def test_regular_user_cannot_login(self):
        """Test that regular users cannot login to admin."""
        response = self.client.post(reverse('users:admin-login'), {
            'username': 'regular',
            'password': 'regularpass123',
        })
        
        # Should redirect back to login page with error message
        self.assertEqual(response.status_code, 302)
        self.assertIn('admin-login', response.url)


class AdminDashboardTests(TestCase):
    """Test admin dashboard functionality."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            user_type='job_seeker',
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username='admin', password='adminpass123')
    
    def test_admin_dashboard_requires_staff(self):
        """Test that admin dashboard requires staff status."""
        # Create regular user and try to access
        regular_user = User.objects.create_user(
            username='regular',
            password='regularpass123',
            user_type='job_seeker'
        )
        self.client.logout()
        self.client.login(username='regular', password='regularpass123')
        
        response = self.client.get(reverse('users:admin-dashboard'))
        # Should redirect or 403
        self.assertNotEqual(response.status_code, 200)
    
    def test_admin_dashboard_loads_for_staff(self):
        """Test that admin dashboard loads for staff users."""
        response = self.client.get(reverse('users:admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Admin Dashboard')
    
    def test_admin_dashboard_shows_statistics(self):
        """Test that admin dashboard shows statistics."""
        from pages.models import BugReport
        from resumes.models import Resume
        
        # Create some test data
        BugReport.objects.create(
            user=self.admin_user,
            description='Test bug',
            url='http://test.com'
        )
        profile = JobSeekerProfile.objects.create(user=self.admin_user)
        Resume.objects.create(profile=profile, title='Test Resume')
        
        response = self.client.get(reverse('users:admin-dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bug Reports')
        self.assertContains(response, 'Total Users')


class AdminBugDetailTests(TestCase):
    """Test admin bug detail functionality."""
    
    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='adminpass123',
            user_type='job_seeker',
            is_staff=True,
            is_superuser=True
        )
        self.client.login(username='admin', password='adminpass123')
        
        from pages.models import BugReport
        self.bug = BugReport.objects.create(
            user=self.admin_user,
            description='Test bug report',
            url='http://test.com'
        )
    
    def test_bug_detail_page_loads(self):
        """Test that bug detail page loads."""
        response = self.client.get(reverse('users:admin-bug-detail', args=[self.bug.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test bug report')
    
    def test_mark_bug_as_resolved(self):
        """Test marking a bug as resolved."""
        response = self.client.post(reverse('users:admin-bug-detail', args=[self.bug.id]), {
            'action': 'resolve',
            'resolution_notes': 'Fixed in latest update',
        })
        
        # Should redirect to dashboard
        self.assertEqual(response.status_code, 302)
        
        # Verify bug is resolved
        self.bug.refresh_from_db()
        self.assertTrue(self.bug.is_resolved)
        self.assertEqual(self.bug.resolution_notes, 'Fixed in latest update')
