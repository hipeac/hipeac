# Generated by Django 2.2.7 on 2019-11-25 10:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("hipeac", "0047_hipeac_visible"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="hipeacpartner",
            name="representatives",
        ),
        migrations.AddField(
            model_name="hipeacpartner",
            name="representative",
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="as_representative",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
