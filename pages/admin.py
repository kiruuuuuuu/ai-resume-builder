from django.contrib import admin
from django.utils import timezone
from .models import BugReport

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
