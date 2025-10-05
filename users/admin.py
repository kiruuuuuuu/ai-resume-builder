from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, JobSeekerProfile, EmployerProfile

class JobSeekerProfileInline(admin.StackedInline):
    """Allows editing the JobSeekerProfile directly from the CustomUser admin page."""
    model = JobSeekerProfile
    can_delete = False
    verbose_name_plural = 'Job Seeker Profile'
    fk_name = 'user'

class EmployerProfileInline(admin.StackedInline):
    """Allows editing the EmployerProfile directly from the CustomUser admin page."""
    model = EmployerProfile
    can_delete = False
    verbose_name_plural = 'Employer Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    """
    A custom admin configuration for our CustomUser model.
    It includes the profile inlines and customizes the list display.
    """
    inlines = (JobSeekerProfileInline, EmployerProfileInline, )
    list_display = ('username', 'email', 'user_type', 'is_staff')
    list_filter = ('user_type', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

# Register the CustomUser model with our custom admin configuration
admin.site.register(CustomUser, CustomUserAdmin)

