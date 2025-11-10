from django.contrib import admin
from django.utils import timezone
from .models import BugReport, Feedback

@admin.register(BugReport)
class BugReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'url_short', 'is_resolved', 'created_at', 'resolved_by']
    list_filter = ['is_resolved', 'created_at']
    search_fields = ['description', 'url', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Report Information', {
            'fields': ('user', 'url', 'description', 'browser_info', 'screenshot', 'created_at')
        }),
        ('Resolution', {
            'fields': ('is_resolved', 'resolved_at', 'resolved_by', 'resolution_notes')
        }),
    )
    
    def url_short(self, obj):
        """Display shortened URL in list view"""
        if len(obj.url) > 50:
            return obj.url[:47] + '...'
        return obj.url
    url_short.short_description = 'URL'
    
    def save_model(self, request, obj, form, change):
        """Auto-set resolved_by and resolved_at when marking as resolved"""
        if obj.is_resolved and not obj.resolved_at:
            obj.resolved_at = timezone.now()
            if not obj.resolved_by:
                obj.resolved_by = request.user
        elif not obj.is_resolved:
            obj.resolved_at = None
            obj.resolved_by = None
        super().save_model(request, obj, form, change)


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'feedback_type', 'rating', 'is_reviewed', 'created_at', 'reviewed_by']
    list_filter = ['feedback_type', 'is_reviewed', 'created_at', 'rating']
    search_fields = ['message', 'user__username', 'user__email']
    readonly_fields = ['created_at']
    fieldsets = (
        ('Feedback Information', {
            'fields': ('user', 'feedback_type', 'message', 'rating', 'created_at')
        }),
        ('Review', {
            'fields': ('is_reviewed', 'reviewed_at', 'reviewed_by', 'admin_notes')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Auto-set reviewed_by and reviewed_at when marking as reviewed"""
        if obj.is_reviewed and not obj.reviewed_at:
            obj.reviewed_at = timezone.now()
            if not obj.reviewed_by:
                obj.reviewed_by = request.user
        elif not obj.is_reviewed:
            obj.reviewed_at = None
            obj.reviewed_by = None
        super().save_model(request, obj, form, change)
