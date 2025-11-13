from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, SetPasswordForm
from django.contrib.auth import password_validation
from .models import CustomUser, JobSeekerProfile, EmployerProfile
from datetime import date, timedelta
import re
import os

class CustomUserCreationForm(UserCreationForm):
    USER_TYPE_CHOICES = (('job_seeker', 'Job Seeker'), ('employer', 'Employer'))
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES, required=True)
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = UserCreationForm.Meta.fields + ('user_type', 'email',)
    
    def clean_password1(self):
        """Validate password strength using Django's built-in validators."""
        password1 = self.cleaned_data.get("password1")
        if password1:
            password_validation.validate_password(password1, self.instance)
        return password1

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = JobSeekerProfile
        fields = ['profile_photo', 'full_name', 'professional_summary', 'phone_number', 'address', 'date_of_birth', 'portfolio_url', 'linkedin_url']
        widgets = {
            'profile_photo': forms.ClearableFileInput(),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'max': date.today().isoformat()}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['email'].initial = self.user.email
        
        if self.instance and self.instance.profile_photo:
            self.fields['profile_photo'].required = False

        # Make other fields mandatory
        self.fields['full_name'].required = True
        self.fields['professional_summary'].required = True
        self.fields['phone_number'].required = True
        self.fields['address'].required = True
        self.fields['date_of_birth'].required = True


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
        if summary:
            if not re.search(r'[a-zA-Z]', summary): raise forms.ValidationError('Professional summary must contain descriptive text.')
            if len(summary.strip()) < 20: raise forms.ValidationError('Professional summary should be at least 20 characters long.')
            # --- THE FIX IS HERE ---
            if len(summary.strip()) > 600: raise forms.ValidationError('Professional summary cannot exceed 600 characters.')
        return summary
        
    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if not phone: return phone
        if not re.match(r'^[0-9\s\-\+\(\)]+$', phone): raise forms.ValidationError('Phone number contains invalid characters.')
        if len(re.sub(r'\D', '', phone)) < 7: raise forms.ValidationError('Please enter a valid phone number.')
        return phone
    
    def clean_address(self):
        address = self.cleaned_data.get('address')
        if address and len(address.strip()) < 10:
            raise forms.ValidationError('Please enter a complete address.')
        return address

    def clean_date_of_birth(self):
        from django.conf import settings
        dob = self.cleaned_data.get('date_of_birth')
        if not dob: return dob
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        min_age = getattr(settings, 'MIN_AGE', 18)
        max_age = getattr(settings, 'MAX_AGE', 100)
        if not (min_age <= age <= max_age):
            raise forms.ValidationError(f'Age must be between {min_age} and {max_age} years old.')
        return dob

    def clean_profile_photo(self):
        photo = self.cleaned_data.get('profile_photo')

        if photo is False:
            return photo 

        if photo:
            if photo.size > 2 * 1024 * 1024: raise forms.ValidationError("Image file too large ( > 2 MB ).")
            if os.path.splitext(photo.name)[1].lower() not in ['.jpg', '.jpeg', '.png']: raise forms.ValidationError("Unsupported file extension. Please use JPG, JPEG, or PNG.")
        
        return photo

class EmployerOnboardingForm(forms.ModelForm):
    """Form for employer onboarding - requires company details."""
    
    class Meta:
        model = EmployerProfile
        fields = ['company_name', 'company_website', 'company_description']
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md'}),
            'company_website': forms.URLInput(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'placeholder': 'https://example.com'}),
            'company_description': forms.Textarea(attrs={'class': 'w-full px-3 py-2 border border-gray-300 rounded-md', 'rows': 5}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['company_name'].required = True
        self.fields['company_website'].required = True
        self.fields['company_description'].required = True
        
        self.fields['company_name'].label = 'Company Name'
        self.fields['company_website'].label = 'Company Website'
        self.fields['company_description'].label = 'Company Description'
    
    def clean_company_name(self):
        name = self.cleaned_data.get('company_name')
        if not name or len(name.strip()) < 2:
            raise forms.ValidationError('Please enter a valid company name.')
        return name.strip()
    
    def clean_company_website(self):
        website = self.cleaned_data.get('company_website')
        if website and not website.startswith(('http://', 'https://')):
            website = 'https://' + website
        return website
    
    def clean_company_description(self):
        desc = self.cleaned_data.get('company_description')
        if desc and len(desc.strip()) < 20:
            raise forms.ValidationError('Company description should be at least 20 characters long.')
        return desc

class UserCredentialsForm(forms.ModelForm):
    """Form for editing user login credentials (username and email)."""
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Enter your username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
                'placeholder': 'Enter your email address'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].required = True
        self.fields['email'].required = True
        self.fields['username'].help_text = 'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            # Check if username is already taken by another user
            if CustomUser.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This username is already taken. Please choose another one.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            if CustomUser.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This email is already registered. Please use another email address.')
        return email

class CustomPasswordChangeForm(forms.Form):
    """Form for changing user password with old password verification."""
    
    old_password = forms.CharField(
        label='Current Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Enter your current password',
            'autocomplete': 'current-password'
        }),
        required=True,
        help_text='Enter your current password to confirm the change.'
    )
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password'
        }),
        required=True,
        help_text=password_validation.password_validators_help_text_html(),
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password'
        }),
        required=True,
        help_text='Enter the same password as above, for verification.',
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('Your current password is incorrect. Please try again.')
        return old_password
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        password_validation.validate_password(password2, self.user)
        return password2
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user

class SetPasswordForm(forms.Form):
    """Form for setting a password for users who don't have one (e.g., social account users)."""
    
    new_password1 = forms.CharField(
        label='New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Enter your new password',
            'autocomplete': 'new-password'
        }),
        required=True,
        help_text=password_validation.password_validators_help_text_html(),
    )
    
    new_password2 = forms.CharField(
        label='Confirm New Password',
        widget=forms.PasswordInput(attrs={
            'class': 'mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm',
            'placeholder': 'Confirm your new password',
            'autocomplete': 'new-password'
        }),
        required=True,
        help_text='Enter the same password as above, for verification.',
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("The two password fields didn't match.")
        password_validation.validate_password(password2, self.user)
        return password2
    
    def save(self, commit=True):
        password = self.cleaned_data['new_password1']
        self.user.set_password(password)
        if commit:
            self.user.save()
        return self.user
