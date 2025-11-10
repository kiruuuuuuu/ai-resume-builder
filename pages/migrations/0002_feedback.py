# Generated migration for Feedback model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pages', '0001_bugreport'),
    ]

    operations = [
        migrations.CreateModel(
            name='Feedback',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feedback_type', models.CharField(choices=[('feature', 'Feature Request'), ('improvement', 'Improvement Suggestion'), ('general', 'General Feedback'), ('other', 'Other')], default='general', help_text='Type of feedback', max_length=20)),
                ('message', models.TextField(help_text='Feedback message')),
                ('rating', models.IntegerField(blank=True, help_text='Rating from 1-5 (optional)', null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_reviewed', models.BooleanField(default=False)),
                ('reviewed_at', models.DateTimeField(blank=True, null=True)),
                ('admin_notes', models.TextField(blank=True, help_text='Admin notes about this feedback', null=True)),
                ('reviewed_by', models.ForeignKey(blank=True, help_text='Admin user who reviewed this feedback', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reviewed_feedback', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, help_text='User who submitted feedback (null if anonymous)', null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Feedback',
                'verbose_name_plural': 'Feedback',
                'ordering': ['-created_at'],
            },
        ),
    ]

