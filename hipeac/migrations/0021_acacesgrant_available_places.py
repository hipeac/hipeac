# Generated by Django 4.2 on 2023-05-03 13:08

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0020_alter_emailrecipient_code_alter_emailrecipient_name"),
    ]

    operations = [
        migrations.AddField(
            model_name="acacesgrant",
            name="available_places",
            field=models.PositiveIntegerField(default=0),
        ),
    ]
