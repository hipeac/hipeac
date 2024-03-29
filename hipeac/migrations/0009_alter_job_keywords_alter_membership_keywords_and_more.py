# Generated by Django 4.1.3 on 2022-11-17 15:44

import django.contrib.postgres.fields

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0008_alter_metadata_options_metadata_keywords"),
    ]

    operations = [
        migrations.AlterField(
            model_name="job",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="membership",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="metadata",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="session",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
        migrations.AlterField(
            model_name="webinar",
            name="keywords",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=190), blank=True, default=list, size=None
            ),
        ),
    ]
