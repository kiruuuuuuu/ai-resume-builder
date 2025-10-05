from django.contrib import admin
from .models import Resume, Experience, Education, Skill, Project, Certification, Achievement, Language, Hobby, ParsedResumeCache

# Register your new model so you can view it in the admin dashboard
admin.site.register(ParsedResumeCache)

# Inlines allow us to edit related models on the same page as the parent model.
class ExperienceInline(admin.TabularInline):
    model = Experience
    extra = 1

class EducationInline(admin.TabularInline):
    model = Education
    extra = 1

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1

class ProjectInline(admin.StackedInline):
    model = Project
    extra = 1

class CertificationInline(admin.TabularInline):
    model = Certification
    extra = 1

class AchievementInline(admin.StackedInline):
    model = Achievement
    extra = 1

class LanguageInline(admin.TabularInline):
    model = Language
    extra = 1

class HobbyInline(admin.TabularInline):
    model = Hobby
    extra = 1

class ResumeAdmin(admin.ModelAdmin):
    """A comprehensive admin view for the Resume model."""
    list_display = ('title', 'profile', 'created_at')
    list_filter = ('profile__user__username',)
    search_fields = ('title', 'profile__user__username')
    inlines = [
        ExperienceInline, EducationInline, SkillInline, ProjectInline,
        CertificationInline, AchievementInline, LanguageInline, HobbyInline
    ]

admin.site.register(Resume, ResumeAdmin)

