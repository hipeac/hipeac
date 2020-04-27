# Generated by Django 2.1.3 on 2018-12-04 10:13

import django.core.validators
from django.db import migrations, models
import hipeac.functions


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0003_auto_20181203_1702"),
    ]

    operations = [
        migrations.AlterField(
            model_name="institution",
            name="image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=hipeac.functions.get_images_path,
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["png"])],
                verbose_name="Logo",
            ),
        ),
        migrations.AlterField(
            model_name="project",
            name="image",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=hipeac.functions.get_images_path,
                validators=[django.core.validators.FileExtensionValidator(allowed_extensions=["png"])],
                verbose_name="Logo",
            ),
        ),
    ]
