# Generated by Django 2.2.9 on 2020-02-17 08:05

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ("hipeac", "0060_auto_20200214_2031"),
    ]

    operations = [
        migrations.AddField(
            model_name="openevent", name="secret", field=models.UUIDField(default=uuid.uuid4, editable=False),
        ),
    ]
