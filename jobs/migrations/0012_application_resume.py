# Generated manually for bug fix: Link applications to specific resume versions

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0011_jobposting_salary_max_jobposting_salary_min'),
        ('resumes', '0011_resume_feedback_resume_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='resume',
            field=models.ForeignKey(blank=True, help_text='The specific resume version used for this application', null=True, on_delete=django.db.models.deletion.SET_NULL, to='resumes.resume'),
        ),
    ]

