# Generated by Django 2.2.2 on 2019-06-05 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hipeac', '0032_auto_20190520_1020'),
    ]

    operations = [
        migrations.AddField(
            model_name='metadata',
            name='euraxess_value',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]