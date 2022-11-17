# Generated by Django 4.0.3 on 2022-04-26 09:11

import django.contrib.postgres.fields
import django.db.models.deletion
import django_countries.fields

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("hipeac", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Member",
            fields=[
                (
                    "keywords",
                    django.contrib.postgres.fields.ArrayField(
                        base_field=models.CharField(max_length=190), blank=True, default=list, editable=False, size=None
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        primary_key=True,
                        related_name="member",
                        serialize=False,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("email", models.EmailField(max_length=254)),
                ("name", models.CharField(max_length=255)),
                ("country", django_countries.fields.CountryField(max_length=2)),
                ("date", models.DateField()),
                (
                    "type",
                    models.CharField(
                        choices=[
                            ("member", "Member"),
                            ("associated_member", "Associated member"),
                            ("affiliated_member", "Affiliated member"),
                            ("affiliated_phd", "Affiliated PhD"),
                        ],
                        max_length=20,
                    ),
                ),
            ],
            options={
                "db_table": "hipeac_membership_member",
                "managed": False,
            },
        ),
        migrations.RunSQL(
            """
            CREATE MATERIALIZED VIEW hipeac_membership_member AS
            SELECT u.id,
                u.id AS user_id,
                u.username,
                u.email,
                concat(u.first_name, ' ', u.last_name) AS name,
                p.country,
                m.date,
                m.type,
                gender.value as gender,
                m.keywords,
                m.advisor_id,
                p.institution_id,
                p.second_institution_id,
                p.is_public
            FROM hipeac_membership m
                JOIN auth_user u ON m.user_id = u.id
                JOIN hipeac_profile p ON u.id = p.user_id
                LEFT JOIN hipeac_metadata gender ON p.gender_id = gender.id
            WHERE m.revocation_date IS NULL AND u.is_active = true
            ORDER BY concat(u.first_name, ' ', u.last_name);
            CREATE UNIQUE INDEX ON hipeac_membership_member (id);
            """,
            "DROP MATERIALIZED VIEW hipeac_membership_member;",
        ),
    ]
