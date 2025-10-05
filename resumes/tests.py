from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.models import JobSeekerProfile
from .forms import (
    ExperienceForm, EducationForm, SkillForm, ProjectForm, CertificationForm,
    AchievementForm, LanguageForm, HobbyForm
)
import datetime


class ResumeFormTests(TestCase):
    """Tests for the forms in the resumes app."""

    def test_experience_form_valid_data(self):
        """Test that the ExperienceForm is valid with correct data."""
        form_data = {
            'job_title': 'Software Engineer',
            'company': 'Google',
            'start_date': '2022-01-01',
            'end_date': '2023-01-01',
            'description': 'Worked on the search algorithm.'
        }
        form = ExperienceForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_experience_form_end_date_before_start_date(self):
        """Test that the form is invalid if the end date is before the start date."""
        form_data = {
            'job_title': 'Software Engineer',
            'company': 'Google',
            'start_date': '2023-01-01',
            'end_date': '2022-01-01',
            'description': 'Time traveler.'
        }
        form = ExperienceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('__all__', form.errors)
        self.assertEqual(form.errors['__all__'][0], "End date cannot be before the start date.")

    def test_experience_form_job_title_has_no_letters(self):
        """Test that the form is invalid if the job title contains no letters."""
        form_data = {
            'job_title': '12345',
            'company': 'Numericorp',
            'start_date': '2022-01-01',
            'description': 'Testing validation.'
        }
        form = ExperienceForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('job_title', form.errors)
        self.assertEqual(form.errors['job_title'][0], 'Job Title must contain descriptive text.')

    def test_education_form_valid_data(self):
        """Test that the EducationForm is valid with correct data."""
        form_data = {
            'institution': 'University of Tech',
            'degree': 'B.S. in Computer Science',
            'field_of_study': 'Computer Science',
            'start_date': '2018-09-01',
            'end_date': '2022-05-01',
            'percentage': '95.5'
        }
        form = EducationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_education_form_invalid_percentage(self):
        """Test that the form is invalid if the percentage is out of range."""
        form_data = {
            'institution': 'University of Testing',
            'degree': 'Degree in Tests',
            'percentage': '101'
        }
        form = EducationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('percentage', form.errors)
        self.assertEqual(form.errors['percentage'][0], 'Percentage must be between 0 and 100.')

    def test_education_form_invalid_institution(self):
        """Test that the form is invalid if the institution name is invalid."""
        form_data = {
            'institution': '777',
            'degree': 'Degree in Numbers'
        }
        form = EducationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('institution', form.errors)
        self.assertEqual(form.errors['institution'][0], 'Institution must contain descriptive text.')

    def test_skill_form_valid_data(self):
        """Test that the SkillForm is valid with correct data."""
        form_data = {'name': 'Python', 'category': 'Backend'}
        form = SkillForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_skill_form_invalid_name(self):
        """Test that the SkillForm is invalid with a numeric-only name."""
        form_data = {'name': '123', 'category': 'Other'}
        form = SkillForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_project_form_valid_data(self):
        """Test that the ProjectForm is valid with correct data."""
        form_data = {
            'title': 'AI Resume Builder',
            'description': 'A web application to build resumes with AI assistance.'
        }
        form = ProjectForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_project_form_invalid_title(self):
        """Test that the ProjectForm is invalid with a title that is too short."""
        form_data = {
            'title': 'AI',
            'description': 'A project.'
        }
        form = ProjectForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)

    def test_certification_form_valid_data(self):
        """Test the CertificationForm with valid data."""
        form_data = {'name': 'Cloud Practitioner', 'issuing_organization': 'Amazon Web Services'}
        form = CertificationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_certification_form_invalid_name(self):
        """Test the CertificationForm with an invalid name."""
        form_data = {'name': '!!', 'issuing_organization': 'AWS'}
        form = CertificationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_achievement_form_valid_data(self):
        """Test the AchievementForm with valid data."""
        form_data = {'name': 'Dean\'s List', 'description': 'Achieved Dean\'s List for three consecutive semesters.'}
        form = AchievementForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_achievement_form_invalid_description(self):
        """Test the AchievementForm with a description that is too short."""
        form_data = {'name': 'Award', 'description': 'Won it.'}
        form = AchievementForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('description', form.errors)

    def test_language_form_valid_data(self):
        """Test the LanguageForm with valid data."""
        form_data = {'name': 'Spanish', 'proficiency': 'Fluent'}
        form = LanguageForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_language_form_invalid_name_has_digits(self):
        """Test the LanguageForm with digits in the name."""
        form_data = {'name': 'Spanish1', 'proficiency': 'Beginner'}
        form = LanguageForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_hobby_form_valid_data(self):
        """Test the HobbyForm with valid data."""
        form_data = {'name': 'Hiking'}
        form = HobbyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_hobby_form_invalid_name(self):
        """Test the HobbyForm with an invalid name."""
        form_data = {'name': '!!'}
        form = HobbyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class ValidateResumeViewTests(TestCase):
	def setUp(self):
		User = get_user_model()
		self.user = User.objects.create_user(username='testuser', email='test@example.com', password='testpass')
		self.client.login(username='testuser', password='testpass')
		# ensure profile exists
		JobSeekerProfile.objects.get_or_create(user=self.user)

	def _set_parsed_data(self, session, data):
		session['parsed_resume_data'] = data
		session.save()

	def test_validate_resume_shows_errors_on_invalid_post(self):
		"""POST invalid data (DOB in the future and numeric-only professional_summary) and expect validation errors."""
		url = reverse('resumes:resume-validate')
		future_date = (datetime.date.today() + datetime.timedelta(days=365)).isoformat()
		parsed = {
			'personal_details': {
				'full_name': 'Test User',
				'email': 'test@example.com',
				'phone_number': '+1 555-555-5555',
				'address': 'Nowhere',
				'date_of_birth': future_date,
			},
			'professional_summary': '1234567890',
			'experience': [], 'education': [], 'skills': [], 'projects': [], 'certifications': [], 'achievements': [], 'languages': [], 'hobbies': []
		}
		sess = self.client.session
		self._set_parsed_data(sess, parsed)

		resp = self.client.post(url, data={
			'profile-full_name': 'Test User',
			'profile-email': 'test@example.com',
			'profile-date_of_birth': future_date,
			'profile-professional_summary': '1234567890',
		})

		# Should not redirect on validation errors; should be 200 and contain error messages
		self.assertEqual(resp.status_code, 200)
		content = resp.content.decode('utf-8')
		self.assertIn('Age must be between 18 and 50 years old.', content)
		self.assertIn('Professional summary must contain descriptive text.', content)

	def test_validate_resume_succeeds_on_valid_post(self):
		"""POST valid data and expect a redirect to the resume builder and resume to be saved."""
		url = reverse('resumes:resume-validate')
		valid_dob = (datetime.date.today() - datetime.timedelta(days=365*25)).isoformat()
		parsed = {
			'personal_details': {
				'full_name': 'Valid User',
				'email': 'valid@example.com',
				'phone_number': '+1 555-555-5555',
				'address': 'Here',
				'date_of_birth': valid_dob,
			},
			'professional_summary': 'Experienced developer with 5 years in web development.',
			'experience': [], 'education': [], 'skills': [], 'projects': [], 'certifications': [], 'achievements': [], 'languages': [], 'hobbies': []
		}
		sess = self.client.session
		self._set_parsed_data(sess, parsed)

		post_data = {
			'profile-full_name': 'Valid User',
			'profile-email': 'valid@example.com',
			'profile-date_of_birth': valid_dob,
			'profile-professional_summary': 'Experienced developer with 5 years in web development.',
		}
		# include empty management forms for each formset so validation passes
		prefixes = ['experience', 'education', 'skill', 'project', 'certification', 'achievement', 'language', 'hobby']
		for p in prefixes:
			post_data[f'{p}-TOTAL_FORMS'] = '0'
			post_data[f'{p}-INITIAL_FORMS'] = '0'
			post_data[f'{p}-MIN_NUM_FORMS'] = '0'
			post_data[f'{p}-MAX_NUM_FORMS'] = '1000'

		resp = self.client.post(url, data=post_data)

		# On success we expect a redirect to resume-builder
		self.assertEqual(resp.status_code, 302)
		self.assertIn(reverse('resumes:resume-builder'), resp['Location'])

