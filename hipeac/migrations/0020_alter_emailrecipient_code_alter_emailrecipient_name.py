# Generated by Django 4.1.6 on 2023-03-31 10:01

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0019_emailrecipient"),
    ]

    operations = [
        migrations.AlterField(
            model_name="emailrecipient",
            name="code",
            field=models.CharField(max_length=64),
        ),
        migrations.AlterField(
            model_name="emailrecipient",
            name="name",
            field=models.CharField(max_length=128),
        ),
    ]
