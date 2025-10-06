from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, JobSeekerProfile
from datetime import date, timedelta
import re
import os

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = (('job_seeker', 'Job Seeker'), ('employer', 'Employer'))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'email',)

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    profile_photo = forms.ImageField(required=True)
    full_name = forms.CharField(required=True)
    professional_summary = forms.CharField(required=True, widget=forms.Textarea)
    phone_number = forms.CharField(required=True)
    address = forms.CharField(required=True)
    date_of_birth = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))


    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['email'].initial = self.user.email
        
        # If a profile picture already exists, make the field not required.
        if self.instance and self.instance.profile_photo:
            self.fields['profile_photo'].required = False
        
    class Meta:
        model = JobSeekerProfile
        fields = ['profile_photo', 'full_name', 'professional_summary', 'phone_number', 'address', 'date_of_birth', 'portfolio_url', 'linkedin_url']
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        if self.user:
            self.user.email = self.cleaned_data['email']
            if commit: self.user.save()
        if commit: profile.save()
        return profile

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name')
        if full_name and re.search(r'\d', full_name): raise forms.ValidationError('Please remove numbers from the name field.')
        if not full_name or len(full_name.strip()) < 2: raise forms.ValidationError('Please enter a valid full name.')
        return full_name

    def clean_professional_summary(self):
        summary = self.cleaned_data.get('professional_summary')
        if not summary:
            raise forms.ValidationError('This field is required.')
        if not re.search(r'[a-zA-Z]', summary): raise forms.ValidationError('Professional summary must contain descriptive text.')
        if len(summary.strip()) < 20: raise forms.ValidationError('Professional summary should be at least 20 characters long.')
        if len(summary.strip()) > 300: raise forms.ValidationError('Professional summary cannot exceed 300 characters.')
        return summary
        
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone: 
            raise forms.ValidationError('This field is required.')
        if not re.match(r'^[0-9\s\-\+\(\)]+$', phone): raise forms.ValidationError('Phone number contains invalid characters.')
        if len(re.sub(r'\D', '', phone)) < 7: raise forms.ValidationError('Please enter a valid phone number.')
        return phone

    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if not dob: 
            raise forms.ValidationError('This field is required.')
        today = date.today(); age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if not (18 <= age <= 50): raise forms.ValidationError('Age must be between 18 and 50 years old.')
        return dob

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')

        # If there's no photo being uploaded AND the field is now optional (because one already exists),
        # then we don't need to validate it.
        if not photo and not self.fields['profile_photo'].required:
            return self.instance.profile_photo # Return the existing photo

        if not photo:
            raise forms.ValidationError('This field is required.')
        if photo.size > 2 * 1024 * 1024: raise forms.ValidationError("Image file too large ( > 2 MB ).")
        if os.path.splitext(photo.name)[1].lower() not in ['.jpg', '.jpeg', '.png']: raise forms.ValidationError("Unsupported file extension. Please use JPG, JPEG, or PNG.")
        return photo

