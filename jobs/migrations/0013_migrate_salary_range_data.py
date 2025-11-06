# Generated manually for salary field refactoring
# Migrates existing salary_range string data to salary_min and salary_max integer fields

from django.db import migrations
import re

def migrate_salary_range_to_min_max(apps, schema_editor):
    """
    Parses existing salary_range string values and populates salary_min and salary_max.
    Handles various formats like:
    - "$80,000 - $100,000"
    - "80000-120000"
    - "$50k - $75k"
    - "50000 to 75000"
    """
    JobPosting = apps.get_model('jobs', 'JobPosting')
    
    for job in JobPosting.objects.filter(salary_range__isnull=False).exclude(salary_range=''):
        salary_range = job.salary_range.strip()
        
        # Skip if already has min/max values
        if job.salary_min is not None or job.salary_max is not None:
            continue
        
        # Extract numbers from the salary range string
        # Remove currency symbols, commas, and common words
        cleaned = re.sub(r'[$,]', '', salary_range.lower())
        cleaned = re.sub(r'\b(per|year|annum|annually|month|monthly|k|thousand)\b', '', cleaned)
        
        # Find all numbers in the string
        numbers = re.findall(r'\d+', cleaned)
        
        if len(numbers) >= 2:
            # If we have at least 2 numbers, use first as min, last as max
            try:
                job.salary_min = int(numbers[0])
                job.salary_max = int(numbers[-1])
                job.save(update_fields=['salary_min', 'salary_max'])
            except (ValueError, TypeError):
                pass
        elif len(numbers) == 1:
            # If only one number, use it as both min and max (or just min)
            try:
                salary_value = int(numbers[0])
                # If it's a large number (likely annual), use as both
                if salary_value > 1000:
                    job.salary_min = salary_value
                    job.salary_max = salary_value
                    job.save(update_fields=['salary_min', 'salary_max'])
            except (ValueError, TypeError):
                pass

def reverse_migration(apps, schema_editor):
    """
    Reverse migration: Convert salary_min/max back to salary_range string format.
    """
    JobPosting = apps.get_model('jobs', 'JobPosting')
    
    for job in JobPosting.objects.filter(salary_min__isnull=False, salary_max__isnull=False):
        if not job.salary_range:
            job.salary_range = f"${job.salary_min:,} - ${job.salary_max:,}"
            job.save(update_fields=['salary_range'])

class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0012_application_resume'),
    ]

    operations = [
        migrations.RunPython(migrate_salary_range_to_min_max, reverse_migration),
    ]

