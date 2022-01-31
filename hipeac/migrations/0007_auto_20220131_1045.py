# Generated by Django 3.2.11 on 2022-01-31 09:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hipeac', '0006_auto_20211203_1231'),
    ]

    operations = [
        migrations.AddField(
            model_name='session',
            name='zoom_attendee_report',
            field=models.FileField(blank=True, null=True, upload_to='private/zoom'),
        ),
        migrations.AddField(
            model_name='session',
            name='zoom_webinar_id',
            field=models.CharField(blank=True, max_length=32, null=True),
        ),
    ]
