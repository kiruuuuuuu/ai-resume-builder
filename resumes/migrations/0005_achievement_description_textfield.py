from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('resumes', '0004_hobby_language'),
    ]

    operations = [
        migrations.AlterField(
            model_name='achievement',
            name='description',
            field=models.TextField(),
        ),
    ]
