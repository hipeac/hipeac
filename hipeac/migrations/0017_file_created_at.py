# Generated by Django 4.1.6 on 2023-02-09 12:02

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0016_jobfaircompany"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
