# Generated by Django 3.0.6 on 2020-05-27 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0077_acacesposterabstract"),
    ]

    operations = [
        migrations.AlterField(
            model_name="acacesposterabstract", name="file", field=models.FileField(upload_to="public/abstract"),
        ),
    ]
