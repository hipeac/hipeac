# Generated by Django 3.0.7 on 2020-06-23 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0080_auto_20200623_0827"),
    ]

    operations = [
        migrations.AddField(model_name="session", name="end_at", field=models.DateTimeField(blank=True, null=True),),
        migrations.AddField(model_name="session", name="start_at", field=models.DateTimeField(blank=True, null=True),),
    ]
