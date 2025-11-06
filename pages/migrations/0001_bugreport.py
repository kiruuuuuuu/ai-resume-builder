# Generated manually for bug reporting feature

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='BugReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(help_text='URL where the bug was encountered', max_length=1024)),
                ('description', models.TextField(help_text='Detailed description of the bug')),
                ('screenshot', models.ImageField(blank=True, help_text='Screenshot of the bug (optional)', null=True, upload_to='bug_reports/')),
                ('browser_info', models.CharField(blank=True, help_text='Browser and version information', max_length=255, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_resolved', models.BooleanField(default=False)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
                ('resolution_notes', models.TextField(blank=True, help_text='Notes about how the bug was resolved', null=True)),
                ('resolved_by', models.ForeignKey(blank=True, help_text='Admin user who resolved this bug', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='resolved_bugs', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, help_text='User who reported the bug (null if anonymous)', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Bug Report',
                'verbose_name_plural': 'Bug Reports',
                'ordering': ['-created_at'],
            },
        ),
    ]

