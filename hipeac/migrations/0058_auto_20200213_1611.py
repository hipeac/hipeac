# Generated by Django 2.2.9 on 2020-02-13 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0057_openregistration_country_raw"),
    ]

    operations = [
        migrations.AddField(
            model_name="openregistration", name="visa_requested", field=models.BooleanField(default=False),
        ),
        migrations.AddField(model_name="openregistration", name="visa_sent", field=models.BooleanField(default=False),),
    ]
