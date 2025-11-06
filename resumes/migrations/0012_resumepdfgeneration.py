# Generated manually for async PDF generation feature

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0011_resume_feedback_resume_score'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResumePDFGeneration',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('template_name', models.CharField(max_length=50)),
                ('accent_color', models.CharField(default='blue', max_length=50)),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('processing', 'Processing'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending', max_length=20)),
                ('task_id', models.CharField(blank=True, help_text='Celery task ID', max_length=255, null=True)),
                ('pdf_file', models.FileField(blank=True, null=True, upload_to='generated_pdfs/')),
                ('error_message', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('resume', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pdf_generations', to='resumes.resume')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='resumepdfgeneration',
            index=models.Index(fields=['resume', 'status'], name='resumes_res_resume__idx'),
        ),
        migrations.AddIndex(
            model_name='resumepdfgeneration',
            index=models.Index(fields=['task_id'], name='resumes_res_task_id_idx'),
        ),
    ]

