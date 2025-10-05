from django import template
from resumes.models import Resume

register = template.Library()

@register.simple_tag
def is_resume_empty(resume: Resume) -> bool:
    """
    Checks if a resume has any content in its related sections.
    Returns True if all sections are empty, False otherwise.
    """
    if not isinstance(resume, Resume):
        return True

    # List of related fields to check
    related_sets = [
        'experience_set', 'education_set', 'skill_set', 'project_set',
        'certification_set', 'achievement_set', 'language_set', 'hobby_set'
    ]
    
    # Check if any of the related sets have items
    for related_set_name in related_sets:
        if hasattr(resume, related_set_name) and getattr(resume, related_set_name).exists():
            return False
            
    # Also check the professional summary
    if resume.profile and resume.profile.professional_summary:
        return False

    return True
