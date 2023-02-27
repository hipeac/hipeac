# Generated by Django 4.0.3 on 2022-04-28 16:40

import django.contrib.postgres.fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0002_member_view"),
    ]

    operations = [
        migrations.CreateModel(
            name="Email",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=64, unique=True)),
                (
                    "action_name",
                    models.CharField(help_text="This text is shown on the admin area dropdowns.", max_length=128),
                ),
                ("position", models.PositiveSmallIntegerField(default=0)),
                ("from_email", models.EmailField(max_length=254, verbose_name="from")),
                (
                    "cc_emails",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.EmailField(max_length=254),
                        blank=True,
                        default=list,
                        size=None,
                        verbose_name="cc",
                    ),
                ),
                ("reply_to_email", models.EmailField(max_length=254, null=True, verbose_name="reply-to")),
                ("subject", models.CharField(max_length=255)),
                ("template", models.TextField()),
            ],
        ),
    ]
