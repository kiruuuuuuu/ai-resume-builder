from django import forms
from .models import Experience, Education, Skill, Project, Certification, Achievement, Language, Hobby
from datetime import date
import re

# --- Validation Helper Functions ---

def _validate_text_field(value, field_label="This field", min_length=3):
    """
    Validates that a field contains letters and is not just punctuation.
    - Allows empty/None values (leave required checks to field.required).
    - Raises ValidationError for invalid input.
    """
    if not value:
        return value
    if not re.search(r'[a-zA-Z]', value):
        raise forms.ValidationError(f'{field_label} must contain descriptive text.')
    if len(value.strip()) < min_length:
        raise forms.ValidationError(f'{field_label} must be at least {min_length} characters long.')
    return value

def _validate_no_digits(value, field_label="This field"):
    """
    Validates that a field does not contain any digits.
    """
    if value and re.search(r'\d', value):
        raise forms.ValidationError(f'Please remove numbers from {field_label.lower()}.')
    return value

def _validate_end_date(cleaned_data, start_date_field='start_date', end_date_field='end_date'):
    """
    Validates that the end date is not before the start date.
    """
    start_date = cleaned_data.get(start_date_field)
    end_date = cleaned_data.get(end_date_field)
    if start_date and end_date and end_date < start_date:
        raise forms.ValidationError("End date cannot be before the start date.")
    return cleaned_data


# --- Forms ---

class UploadResumeForm(forms.Form):
    resume_file = forms.FileField(label="Upload your Resume (PDF or DOCX)")

class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        fields = ['job_title', 'company', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_job_title(self):
        return _validate_no_digits(_validate_text_field(self.cleaned_data.get('job_title'), 'Job Title'), 'Job Title')
    
    def clean_company(self):
        return _validate_no_digits(_validate_text_field(self.cleaned_data.get('company'), 'Company'), 'Company')
    
    def clean_description(self):
        return _validate_text_field(self.cleaned_data.get('description'), 'Description', min_length=10)

    def clean(self):
        return _validate_end_date(super().clean())

class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        fields = ['institution', 'degree', 'field_of_study', 'start_date', 'end_date', 'percentage', 'address']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
            'percentage': forms.NumberInput(attrs={'min': 0, 'max': 100, 'step': 0.1, 'placeholder': 'e.g., 85.5 or 8.5'}),
        }
    
    def clean_institution(self):
        return _validate_text_field(self.cleaned_data.get('institution'), 'Institution')

    def clean_degree(self):
        return _validate_text_field(self.cleaned_data.get('degree'), 'Degree')

    def clean_field_of_study(self):
        return _validate_text_field(self.cleaned_data.get('field_of_study'), 'Field of Study', min_length=2)
    
    def clean_percentage(self):
        percentage = self.cleaned_data.get('percentage')
        if percentage:
            try:
                p_float = float(percentage)
                if not (0 <= p_float <= 100):
                    raise forms.ValidationError("Percentage must be between 0 and 100.")
            except (ValueError, TypeError):
                raise forms.ValidationError("Please enter a valid number for percentage.")
        return percentage

    def clean(self):
        return _validate_end_date(super().clean())

class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        fields = ['name', 'category']
    
    def clean_name(self):
        return _validate_text_field(self.cleaned_data.get('name'), 'Skill Name')

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'aim', 'frontend', 'backend', 'database', 'link']

    def clean_title(self):
        return _validate_text_field(self.cleaned_data.get('title'), 'Project Title')

    def clean_description(self):
        return _validate_text_field(self.cleaned_data.get('description'), 'Description', min_length=10)

class CertificationForm(forms.ModelForm):
    class Meta:
        model = Certification
        fields = ['name', 'issuing_organization', 'date_issued']
        widgets = {'date_issued': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()})}
    
    def clean_name(self):
        return _validate_text_field(self.cleaned_data.get('name'), 'Certification Name')

    def clean_issuing_organization(self):
        return _validate_text_field(self.cleaned_data.get('issuing_organization'), 'Issuing Organization')

class AchievementForm(forms.ModelForm):
    class Meta:
        model = Achievement
        fields = ['name', 'description']
    
    def clean_name(self):
        return _validate_text_field(self.cleaned_data.get('name'), 'Achievement Title')
        
    def clean_description(self):
        return _validate_text_field(self.cleaned_data.get('description'), 'Description', min_length=10)

class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        fields = ['name', 'proficiency']

    def clean_name(self):
        return _validate_no_digits(_validate_text_field(self.cleaned_data.get('name'), 'Language'), 'Language')

class HobbyForm(forms.ModelForm):
    class Meta:
        model = Hobby
        fields = ['name']

    def clean_name(self):
        return _validate_text_field(self.cleaned_data.get('name'), 'Hobby')
