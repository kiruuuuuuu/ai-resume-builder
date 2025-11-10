# Generated migration for adding pdf_content field to ResumePDFGeneration

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0012_resumepdfgeneration'),
    ]

    operations = [
        migrations.AddField(
            model_name='resumepdfgeneration',
            name='pdf_content',
            field=models.BinaryField(blank=True, help_text='PDF content stored in database for Railway compatibility', null=True),
        ),
    ]

