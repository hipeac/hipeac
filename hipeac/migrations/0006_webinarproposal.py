# Generated by Django 4.1.1 on 2022-09-16 09:54

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0005_alter_email_from_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="WebinarProposal",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("uuid", models.UUIDField(default=uuid.uuid4, editable=False)),
                ("first_name", models.CharField(max_length=250)),
                ("last_name", models.CharField(max_length=250)),
                ("email", models.EmailField(max_length=254)),
                ("title", models.CharField(max_length=250)),
                ("organizers", models.TextField()),
                ("summary", models.TextField()),
                ("projects", models.TextField(blank=True, null=True)),
                ("duration", models.CharField(max_length=250)),
                ("session_format", models.CharField(blank=True, max_length=250, null=True)),
                ("expected_attendees", models.CharField(max_length=250)),
                ("previous_editions", models.TextField(blank=True, null=True)),
                ("other", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "hipeac_webinar_proposal",
            },
        ),
    ]