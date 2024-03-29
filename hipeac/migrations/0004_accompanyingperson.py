# Generated by Django 4.0.3 on 2022-06-03 09:33

import django.db.models.deletion

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("hipeac", "0003_email"),
    ]

    operations = [
        migrations.CreateModel(
            name="AccompanyingPerson",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=255)),
                (
                    "meal_preference",
                    models.ForeignKey(
                        blank=True,
                        limit_choices_to={"type": "meal_preference"},
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="accompanier_meal_preference",
                        to="hipeac.metadata",
                    ),
                ),
                (
                    "registration",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accompanying_persons",
                        to="hipeac.registration",
                    ),
                ),
            ],
            options={
                "db_table": "hipeac_event_registration_accompanier",
            },
        ),
    ]
