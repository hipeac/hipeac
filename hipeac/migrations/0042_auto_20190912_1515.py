# Generated by Django 2.2.5 on 2019-09-12 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hipeac', '0041_auto_20190912_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='link',
            name='type',
            field=models.CharField(choices=[('website', 'Website'), ('dblp', 'DBLP'), ('linkedin', 'LinkedIn'), ('github', 'GitHub'), ('twitter', 'Twitter'), ('youtube', 'YouTube'), ('easychair', 'EasyChair'), ('cordis', 'Cordis'), ('google_maps', 'Google Maps'), ('google_photos', 'Google Photos'), ('other', 'Other')], max_length=32),
        ),
    ]
