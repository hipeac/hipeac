# Generated by Django 4.1.4 on 2023-01-13 10:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hipeac", "0014_file_keywords"),
    ]

    operations = [
        migrations.AddField(
            model_name="techtransferaward",
            name="has_price_money",
            field=models.BooleanField(default=True, help_text="Only once per awardee."),
        ),
        migrations.AlterField(
            model_name="techtransferaward",
            name="awardee",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="tech_transfer_awards",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
