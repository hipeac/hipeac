# Generated by Django 2.2.6 on 2019-10-14 09:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0044_auto_20190927_1151"),
    ]

    operations = [
        migrations.RemoveField(model_name="techtransferapplication", name="status",),
        migrations.AddField(
            model_name="techtransferapplication", name="awarded", field=models.BooleanField(default=None, null=True),
        ),
    ]
