# Generated migration for adding pdf_content field to ResumePDFGeneration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0013_rename_resumes_res_resume__idx_resumes_res_resume__4807cf_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumepdfgeneration',
            name='pdf_content',
            field=models.BinaryField(blank=True, help_text='PDF content stored in database for Railway compatibility', null=True),
        ),
    ]

