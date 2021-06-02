# Generated by Django 3.1.2 on 2020-11-02 15:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0090_auto_20201008_1338"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="session", options={"ordering": ["start_at", "session_type__position", "room__position", "end_at"]},
        ),
        migrations.AddField(
            model_name="session",
            name="zoom_attendee_report",
            field=models.FileField(blank=True, null=True, upload_to="private/zoom"),
        ),
    ]