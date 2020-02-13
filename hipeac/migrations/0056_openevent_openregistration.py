# Generated by Django 2.2.9 on 2020-02-13 10:15

from django.db import migrations, models
import django.db.models.deletion
import django_countries.fields
import hipeac.functions
import hipeac.models.mixins
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('hipeac', '0055_auto_20200213_1114'),
    ]

    operations = [
        migrations.CreateModel(
            name='OpenEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('registration_start_date', models.DateField()),
                ('registration_deadline', models.DateTimeField()),
                ('name', models.CharField(max_length=100)),
                ('presentation', models.TextField(blank=True, null=True)),
                ('city', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(db_index=True, max_length=2)),
                ('hashtag', models.CharField(blank=True, max_length=32, null=True)),
                ('custom_url', models.URLField(help_text='https://events.hipeac.net/...', null=True)),
                ('image', models.FileField(blank=True, help_text='4:1 format', null=True, upload_to=hipeac.functions.get_images_path, verbose_name='Banner')),
                ('travel_info', models.TextField(blank=True, null=True)),
                ('registrations_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['-start_date'],
            },
            bases=(hipeac.models.mixins.ImagesMixin, hipeac.models.mixins.LinkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='OpenRegistration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('first_name', models.CharField(max_length=250)),
                ('last_name', models.CharField(max_length=250)),
                ('email', models.EmailField(max_length=254)),
                ('affiliation', models.CharField(max_length=250)),
                ('address', models.CharField(blank=True, max_length=250, null=True)),
                ('zip_code', models.CharField(blank=True, max_length=250, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('bool_q1', models.BooleanField(default=False)),
                ('bool_q2', models.BooleanField(default=False)),
                ('bool_q3', models.BooleanField(default=False)),
                ('bool_q4', models.BooleanField(default=False)),
                ('open_q1', models.TextField(blank=True, null=True)),
                ('open_q2', models.TextField(blank=True, null=True)),
                ('open_q3', models.TextField(blank=True, null=True)),
                ('open_q4', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='hipeac.OpenEvent')),
            ],
        ),
    ]