# Generated by Django 3.1.5 on 2021-01-12 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0091_auto_20201102_1637"),
    ]

    operations = [
        migrations.AddField(model_name="registration", name="custom_data", field=models.JSONField(default=dict),),
    ]