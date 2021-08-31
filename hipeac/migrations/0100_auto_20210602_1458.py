# Generated by Django 3.2.2 on 2021-06-02 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0099_course_custom_data"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="break",
            options={"ordering": ["start_at"]},
        ),
        migrations.RemoveField(
            model_name="break",
            name="date",
        ),
        migrations.AlterField(
            model_name="break",
            name="end_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="break",
            name="start_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
