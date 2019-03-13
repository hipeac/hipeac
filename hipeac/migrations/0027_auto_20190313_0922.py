# Generated by Django 2.1.7 on 2019-03-13 08:22

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('hipeac', '0026_internshipapplication_selected'),
    ]

    operations = [
        migrations.CreateModel(
            name='TechTransferApplication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('OK', 'Awarded'), ('NO', 'Rejected'), ('UN', 'Pending')], default='UN', max_length=2)),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField(verbose_name='Description of the technology being transferred')),
                ('partners_description', models.TextField(verbose_name='Description of the academic partners and the company involved')),
                ('value', models.TextField(verbose_name='Estimate of the value of the agreement')),
                ('awarded_summary', models.TextField(help_text='Summary, if awarded, to show online.', null=True, verbose_name='Summary')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('applicant', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='technology_transfer_award_applications', to=settings.AUTH_USER_MODEL)),
                ('awarded_from', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ttawards_from', to='hipeac.Institution')),
                ('awarded_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ttawards_to', to='hipeac.Institution')),
                ('awardee', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='technology_transfer_financial_award', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='TechTransferCall',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_frozen', models.BooleanField(default=False, help_text='Check this box to avoid further editing on applications.')),
            ],
            options={
                'ordering': ('-start_date',),
            },
        ),
        migrations.AddField(
            model_name='techtransferapplication',
            name='call',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='hipeac.TechTransferCall'),
        ),
        migrations.AddField(
            model_name='techtransferapplication',
            name='team',
            field=models.ManyToManyField(blank=True, help_text='Team members that will receive an award (certificate).', related_name='technology_transfer_awards', to=settings.AUTH_USER_MODEL),
        ),
    ]