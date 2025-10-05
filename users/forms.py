from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, JobSeekerProfile
from datetime import date, timedelta
import re
import os

class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating new users, adding the user_type field.
    """
    USER_TYPE_CHOICES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'email',)

class ProfileUpdateForm(forms.ModelForm):
    """
    A form for users to update their personal profile details.
    """
    # Add the email field here to include it in the form
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm'}))

    def __init__(self, *args, **kwargs):
        # Pop the user instance from kwargs to prevent it from going to the ModelForm
        self.user = kwargs.pop('user', None)
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)

        # Populate the email field with the user's current email
        if self.user:
            self.fields['email'].initial = self.user.email

        # Make non-essential fields optional
        required_fields = ['full_name', 'email']
        for field_name, field in self.fields.items():
            if field_name not in required_fields:
                field.required = False
        
        # Add client-side max for date_of_birth to prevent future dates
        if 'date_of_birth' in self.fields:
            today = date.today()
            eighteen_years_ago = today - timedelta(days=18*365.25)
            fifty_years_ago = today - timedelta(days=50*365.25)
            dob_attrs = self.fields['date_of_birth'].widget.attrs
            dob_attrs['max'] = eighteen_years_ago.isoformat()
            dob_attrs['min'] = fifty_years_ago.isoformat()

    class Meta:
        model = JobSeekerProfile
        fields = [
            'profile_photo', 'full_name', 'professional_summary',
            'phone_number', 'address', 'date_of_birth', 'portfolio_url', 'linkedin_url'
        ]
        widgets = {
            'profile_photo': forms.ClearableFileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100'}),
            'full_name': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Your full name as you want it to appear on the resume.', 'inputmode': 'text', 'pattern': '.*[A-Za-z].*', 'minlength': 2, 'title': 'Please enter your name (letters required).', 'data-no-digits': '1'}),
            'professional_summary': forms.Textarea(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'rows': 4, 'placeholder': 'A 1-3 sentence summary...'}),
            'phone_number': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Optional: e.g., +1 555-555-5555.', 'inputmode': 'tel', 'pattern': '^[0-9\\s\\-\\+\\(\\)]+$', 'title': 'Enter a valid phone number.'}),
            'address': forms.TextInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Optional: e.g., San Francisco, CA'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'type': 'date'}),
            'portfolio_url': forms.URLInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Optional: e.g., https://github.com/your-username'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm', 'placeholder': 'Optional: e.g., https://linkedin.com/in/your-profile'}),
        }
        help_texts = {'profile_photo': 'Optional: a square professional headshot (JPEG/PNG).'}

    def save(self, commit=True):
        # Save the JobSeekerProfile instance
        profile = super().save(commit=False)
        
        # Save the email to the CustomUser instance
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit:
                self.user.save()
        
        if commit:
            profile.save()
            
        return profile

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and re.search(r'\d', full_name):
            raise forms.ValidationError('Please remove numbers from the name field.')
        if not full_name or len(full_name.strip()) < 2:
             raise forms.ValidationError('Please enter a valid full name.')
        return full_name

    def clean_professional_summary(self):
        summary = self.cleaned_data.get('professional_summary')
        if summary:
            if not re.search(r'[a-zA-Z]', summary):
                raise forms.ValidationError('Professional summary must contain descriptive text.')
            if len(summary.strip()) < 20:
                raise forms.ValidationError('Professional summary should be at least 20 characters long.')
        return summary
        
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone:
            return phone
        if not re.match(r'^[0-9\s\-\+\(\)]+$', phone):
            raise forms.ValidationError('Phone number contains invalid characters.')
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 7:
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone

    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address:
            if not re.search(r'[a-zA-Z0-9]', address):
                raise forms.ValidationError('Please enter a valid address.')
        return address

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob:
            return dob
        
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        
        if not (18 <= age <= 50):
            raise forms.ValidationError('Age must be between 18 and 50 years old.')
        return dob

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')
        if photo:
            # Check file size (e.g., 2.5 MB limit)
            if photo.size > 2.5 * 1024 * 1024:
                raise forms.ValidationError("Image file too large ( > 2.5 MB ).")
            # Check file type
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(photo.name)[1]
            if ext.lower() not in valid_extensions:
                raise forms.ValidationError("Unsupported file extension. Please use JPG, JPEG, or PNG.")
        return photo

