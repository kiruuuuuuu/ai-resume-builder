from django import template
from resumes.models import Resume

register = template.Library()


def get_resume_completeness_errors(resume: Resume) -> list:
    """
    Checks for the minimum required content and returns a list of missing items.
    A valid resume for applying requires a summary, at least one education entry, and at least one skill.
    """
    errors = []
    if not isinstance(resume, Resume):
        errors.append("a resume has not been created yet")
        return errors

    # Check for the three core components of a minimum viable resume.
    if not (resume.profile and resume.profile.professional_summary and len(resume.profile.professional_summary.strip()) > 20):
        errors.append("a professional summary")
    
    if not resume.education_set.exists():
        errors.append("at least one education entry")

    if not resume.skill_set.exists():
        errors.append("at least one skill")
        
    return errors


@register.simple_tag
def is_resume_empty(resume: Resume) -> bool:
    """
    Checks if a resume has any content in its related sections.
    This is used for display logic, not for application validation.
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
