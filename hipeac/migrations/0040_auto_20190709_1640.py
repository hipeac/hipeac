# Generated by Django 2.2.3 on 2019-07-09 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0039_job_show_in_euraxess"),
    ]

    operations = [
        migrations.AlterField(model_name="job", name="add_to_euraxess", field=models.BooleanField(default=True),),
    ]
