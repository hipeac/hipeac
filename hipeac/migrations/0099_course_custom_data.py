# Generated by Django 3.2.2 on 2021-06-01 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0098_auto_20210219_1604"),
    ]

    operations = [
        migrations.AddField(model_name="course", name="custom_data", field=models.JSONField(default=dict),),
    ]