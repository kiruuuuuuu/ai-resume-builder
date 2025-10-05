from django.contrib import admin
from .models import JobPosting, Application, Notification, Interview

class ApplicationInline(admin.TabularInline):
    """Shows applications directly on the Job Posting admin page."""
    model = Application
    extra = 0 # Don't show extra forms for adding new applications here
    fields = ('applicant', 'status', 'applied_at')
    readonly_fields = ('applicant', 'applied_at')
    can_delete = False

class JobPostingAdmin(admin.ModelAdmin):
    """Customizes the admin view for Job Postings."""
    list_display = ('title', 'employer', 'location', 'created_at', 'application_deadline')
    list_filter = ('employer__company_name', 'location')
    search_fields = ('title', 'description', 'requirements')
    ordering = ('-created_at',)
    inlines = [ApplicationInline]

class ApplicationAdmin(admin.ModelAdmin):
    """Customizes the admin view for Applications."""
    list_display = ('applicant', 'job_posting', 'status', 'applied_at')
    list_filter = ('status', 'job_posting__title')
    search_fields = ('applicant__user__username', 'job_posting__title')
    ordering = ('-applied_at',)

class NotificationAdmin(admin.ModelAdmin):
    """Customizes the admin view for Notifications."""
    list_display = ('recipient', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('recipient__username', 'message')

class InterviewAdmin(admin.ModelAdmin):
    """Customizes the admin view for Interviews."""
    list_display = ('application', 'status', 'confirmed_slot')
    list_filter = ('status',)

admin.site.register(JobPosting, JobPostingAdmin)
admin.site.register(Application, ApplicationAdmin)
admin.site.register(Notification, NotificationAdmin)
admin.site.register(Interview, InterviewAdmin)
