from django.db import models
from django.conf import settings

class BugReport(models.Model):
    """
    Model to store bug reports submitted by users with optional screenshots.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who reported the bug (null if anonymous)")
    url = models.URLField(max_length=1024, help_text="URL where the bug was encountered")
    description = models.TextField(help_text="Detailed description of the bug")
    screenshot = models.ImageField(upload_to='bug_reports/', null=True, blank=True, help_text="Screenshot of the bug (optional)")
    browser_info = models.CharField(max_length=255, null=True, blank=True, help_text="Browser and version information")
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='resolved_bugs', help_text="Admin user who resolved this bug")
    resolution_notes = models.TextField(null=True, blank=True, help_text="Notes about how the bug was resolved")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bug Report"
        verbose_name_plural = "Bug Reports"

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        status = "Resolved" if self.is_resolved else "Open"
        return f"Bug #{self.id} - {user_str} - {status}"


class Feedback(models.Model):
    """
    Model to store user feedback and suggestions.
    """
    FEEDBACK_TYPES = [
        ('feature', 'Feature Request'),
        ('improvement', 'Improvement Suggestion'),
        ('general', 'General Feedback'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, help_text="User who submitted feedback (null if anonymous)")
    feedback_type = models.CharField(max_length=20, choices=FEEDBACK_TYPES, default='general', help_text="Type of feedback")
    message = models.TextField(help_text="Feedback message")
    rating = models.IntegerField(null=True, blank=True, help_text="Rating from 1-5 (optional)")
    created_at = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_feedback', help_text="Admin user who reviewed this feedback")
    admin_notes = models.TextField(null=True, blank=True, help_text="Admin notes about this feedback")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Feedback"
        verbose_name_plural = "Feedback"

    def __str__(self):
        user_str = self.user.username if self.user else "Anonymous"
        return f"Feedback #{self.id} - {user_str} - {self.get_feedback_type_display()}"