# Generated by Django 2.1.5 on 2019-02-08 11:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0020_auto_20190208_1151"),
    ]

    operations = [
        migrations.AddField(
            model_name="vision",
            name="flyer",
            field=models.FileField(blank=True, null=True, upload_to="public/vision"),
        ),
    ]
