# Generated by Django 2.2.2 on 2019-06-17 06:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0035_magazine_downloads"),
    ]

    operations = [
        migrations.AlterField(
            model_name="magazine",
            name="file",
            field=models.FileField(blank=True, null=True, upload_to="private/magazine"),
        ),
        migrations.AlterField(
            model_name="magazine",
            name="file_tablet",
            field=models.FileField(blank=True, null=True, upload_to="private/magazine"),
        ),
        migrations.AlterField(
            model_name="vision", name="file", field=models.FileField(blank=True, null=True, upload_to="private/vision"),
        ),
        migrations.AlterField(
            model_name="vision",
            name="file_draft",
            field=models.FileField(blank=True, null=True, upload_to="private/vision"),
        ),
    ]
