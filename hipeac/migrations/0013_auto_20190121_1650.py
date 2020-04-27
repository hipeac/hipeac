# Generated by Django 2.1.5 on 2019-01-21 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0012_registration_manual_extra_fees"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="session", options={"ordering": ["date", "start_at", "room__position", "end_at"]},
        ),
        migrations.RemoveField(model_name="video", name="project",),
        migrations.AddField(
            model_name="video",
            name="projects",
            field=models.ManyToManyField(blank=True, related_name="videos", to="hipeac.Project"),
        ),
    ]
