# Generated by Django 2.1.4 on 2018-12-19 13:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hipeac', '0010_session_institutions'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='keywords',
            field=models.TextField(default='[]', editable=False),
        ),
    ]