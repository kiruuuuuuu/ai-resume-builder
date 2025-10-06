from django import forms
from .models import JobPosting
from django.utils import timezone
import re

# --- Validation Helper Functions ---

def _validate_text_field(value, field_label="This field", min_length=3):
    """
    Validates that a field contains letters and is not just punctuation.
    """
    if not value:
        return value
    if not re.search(r'[a-zA-Z]', value):
        raise forms.ValidationError(f'{field_label} must contain descriptive text.')
    if len(value.strip()) < min_length:
        raise forms.ValidationError(f'{field_label} must be at least {min_length} characters long.')
    return value

# --- Forms ---

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = ['title', 'description', 'requirements', 'location', 'salary_range', 'vacancies', 'application_deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'rows': 5}),
            'requirements': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'rows': 5}),
            'location': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}),
            'salary_range': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'e.g., $80,000 - $100,000 per year'}),
            'vacancies': forms.NumberInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'min': 1}),
            'application_deadline': forms.DateTimeInput(
                attrs={
                    'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 
                    'type': 'datetime-local'
                }
            ),
        }

    def clean_title(self):
        return _validate_text_field(self.cleaned_data.get('title'), 'Title', min_length=5)

    def clean_description(self):
        return _validate_text_field(self.cleaned_data.get('description'), 'Description', min_length=30)

    def clean_requirements(self):
        return _validate_text_field(self.cleaned_data.get('requirements'), 'Requirements', min_length=20)

    def clean_location(self):
        return _validate_text_field(self.cleaned_data.get('location'), 'Location')
        
    def clean_salary_range(self):
        salary = self.cleaned_data.get('salary_range')
        if salary and not re.search(r'\d', salary):
            raise forms.ValidationError('Salary range must contain a number.')
        return salary

    def clean_application_deadline(self):
        deadline = self.cleaned_data.get('application_deadline')
        if deadline and deadline < timezone.now():
            raise forms.ValidationError("Application deadline cannot be in the past.")
        return deadline

class InterviewSlotForm(forms.Form):
    """
    A form for a single interview time slot proposal
    """
    proposed_time = forms.DateTimeField(
        required=False,
        label="Proposed Time Slot",
        widget=forms.DateTimeInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'type': 'datetime-local'
        })
    )
    interview_details = forms.CharField(
        required=False,
        label="Interview Details (e.g., Google Meet link, address)",
        widget=forms.Textarea(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'rows': 3
        })
    )

    def clean_proposed_time(self):
        time = self.cleaned_data.get('proposed_time')
        if time and time < timezone.now():
            raise forms.ValidationError("Proposed interview time cannot be in the past.")
        return time

    def clean_interview_details(self):
        return _validate_text_field(self.cleaned_data.get('interview_details'), 'Interview Details', min_length=10)

