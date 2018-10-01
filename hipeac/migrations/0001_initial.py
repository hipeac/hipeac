# Generated by Django 2.1.2 on 2018-10-01 12:59

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import hipeac.functions
import hipeac.models.generic
import hipeac.models.mixins
import hipeac.models.users
import hipeac.validators
import re
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('flatpages', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0009_alter_user_last_name_max_length'),
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ready', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('blog', 'HiPEAC Blog'), ('news', 'HiPEAC News'), ('release', 'HiPEAC Press Release'), ('jobs', 'HiPEAC Career News')], default='news', max_length=7)),
                ('publication_date', models.DateField()),
                ('title', models.CharField(max_length=250)),
                ('excerpt', models.TextField()),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField()),
            ],
            options={
                'ordering': ['-publication_date'],
            },
            bases=(hipeac.models.mixins.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Block',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=32)),
                ('notes', models.CharField(max_length=255)),
                ('header', models.TextField(blank=True)),
                ('content', models.TextField()),
            ],
            options={
                'verbose_name': 'page block',
                'ordering': ['page', 'key'],
            },
        ),
        migrations.CreateModel(
            name='Clipping',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('media', models.CharField(max_length=250)),
                ('title', models.CharField(max_length=250)),
                ('url', models.URLField()),
                ('publication_date', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-publication_date'],
            },
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('value', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
                ('notes', models.CharField(blank=True, max_length=190, null=True)),
                ('created_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['event', 'id'],
            },
        ),
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('registration_start_date', models.DateField()),
                ('registration_early_deadline', models.DateTimeField(blank=True, null=True)),
                ('registration_deadline', models.DateTimeField()),
                ('type', models.CharField(choices=[('csw', 'CSW'), ('conference', 'Conference'), ('acaces', 'ACACES Summer School'), ('ec_meeting', 'EC Consultation Meeting')], editable=False, max_length=16)),
                ('city', models.CharField(max_length=100)),
                ('country', django_countries.fields.CountryField(db_index=True, max_length=2)),
                ('hashtag', models.CharField(blank=True, max_length=32, null=True)),
                ('slug', models.CharField(editable=False, max_length=100)),
                ('redirect_url', models.URLField(editable=False, null=True)),
                ('image', models.FileField(blank=True, help_text='4:1 format', null=True, upload_to=hipeac.functions.get_images_path, verbose_name='Banner')),
                ('registrations_count', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ['-start_date'],
            },
            bases=(hipeac.models.mixins.ImagesMixin, hipeac.models.mixins.LinkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Fee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('early', 'Early'), ('late', 'Late'), ('early_student', 'Early (student)'), ('late_student', 'Late (student)'), ('late_student', 'Booth fee')], editable=False, max_length=16)),
                ('value', models.PositiveIntegerField(default=0, validators=[django.core.validators.MinValueValidator(1)])),
                ('notes', models.CharField(blank=True, max_length=190, null=True)),
            ],
            options={
                'db_table': 'hipeac_event_fee',
            },
        ),
        migrations.CreateModel(
            name='Image',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.FileField(blank=True, null=True, upload_to='public/images', verbose_name='Image')),
                ('position', models.PositiveSmallIntegerField()),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['content_type', 'object_id', 'position'],
            },
        ),
        migrations.CreateModel(
            name='Institution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=190)),
                ('local_name', models.CharField(blank=True, max_length=190, null=True)),
                ('colloquial_name', models.CharField(blank=True, max_length=30, null=True)),
                ('type', models.CharField(choices=[('university', 'University'), ('lab', 'Government Lab'), ('innovation', 'Innovation Center'), ('industry', 'Industry'), ('sme', 'SME'), ('other', 'Other')], max_length=16)),
                ('location', models.CharField(blank=True, max_length=100, null=True)),
                ('country', django_countries.fields.CountryField(db_index=True, max_length=2)),
                ('description', models.TextField(blank=True, null=True, validators=[hipeac.validators.validate_no_badwords])),
                ('recruitment_contact', models.CharField(blank=True, max_length=190, null=True)),
                ('recruitment_email', models.EmailField(blank=True, max_length=254, null=True)),
                ('image', models.FileField(blank=True, null=True, upload_to=hipeac.functions.get_images_path, verbose_name='Logo')),
                ('application_areas', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('topics', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('updated_at', models.DateTimeField()),
            ],
            options={
                'ordering': ['name'],
            },
            bases=(hipeac.models.mixins.ImagesMixin, hipeac.models.mixins.LinkMixin, hipeac.models.mixins.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250, validators=[hipeac.validators.validate_no_badwords])),
                ('description', models.TextField(validators=[hipeac.validators.validate_no_badwords])),
                ('deadline', models.DateField(null=True)),
                ('positions', models.PositiveSmallIntegerField(default=1, null=True)),
                ('location', models.CharField(blank=True, max_length=250, null=True)),
                ('country', django_countries.fields.CountryField(blank=True, countries=hipeac.models.generic.HipeacCountries, db_index=True, max_length=2, null=True)),
                ('email', models.EmailField(max_length=254, null=True)),
                ('share', models.BooleanField(default=True, editable=False)),
                ('application_areas', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('career_levels', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('topics', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('keywords', models.TextField(blank=True, editable=False, null=True)),
                ('last_reminder', models.DateTimeField(blank=True, editable=False, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ('-created_at',),
            },
            bases=(hipeac.models.mixins.LinkMixin, hipeac.models.mixins.MetadataMixin, hipeac.models.mixins.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('website', 'Website'), ('dblp', 'DBLP'), ('twitter', 'Twitter'), ('linkedin', 'LinkedIn'), ('github', 'GitHub'), ('youtube', 'YouTube'), ('google_maps', 'Google Maps'), ('google_photos', 'Google Photos'), ('easychair', 'EasyChair'), ('other', 'Other')], max_length=32)),
                ('url', models.URLField()),
                ('object_id', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['-type'],
            },
        ),
        migrations.CreateModel(
            name='MailingList',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=160)),
                ('password', models.CharField(max_length=160)),
                ('query', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ['code'],
            },
        ),
        migrations.CreateModel(
            name='Metadata',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('gender', 'Gender'), ('title', 'Title'), ('meal_preference', 'Meal preference'), ('job_position', 'Position'), ('employment_type', 'Employment type'), ('application_area', 'Application area'), ('topic', 'Topic')], max_length=32)),
                ('value', models.CharField(max_length=64)),
                ('position', models.PositiveSmallIntegerField(default=0)),
            ],
            options={
                'ordering': ['type', 'value'],
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('flatpage_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='flatpages.FlatPage')),
            ],
            bases=('flatpages.flatpage',),
        ),
        migrations.CreateModel(
            name='Permission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.PositiveSmallIntegerField(choices=[(9, 'Owner'), (7, 'Administrator'), (1, 'Guest')], db_index=True)),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='xpermissions', to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='profile', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('bio', models.TextField(blank=True, null=True)),
                ('country', django_countries.fields.CountryField(db_index=True, max_length=2)),
                ('department', models.CharField(blank=True, max_length=200, null=True)),
                ('membership_tags', models.CharField(blank=True, max_length=250, null=True, validators=[hipeac.models.users.validate_membership_tags])),
                ('membership_date', models.DateField(blank=True, null=True)),
                ('membership_revocation_date', models.DateField(blank=True, null=True)),
                ('is_bouncing', models.BooleanField(default=False)),
                ('is_subscribed', models.BooleanField(default=False)),
                ('is_public', models.BooleanField(default=False)),
                ('application_areas', models.CharField(blank=True, default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('topics', models.CharField(blank=True, default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('advisor', models.ForeignKey(blank=True, limit_choices_to={'profile__membership_tags__contains': 'member'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='affiliates', to=settings.AUTH_USER_MODEL)),
                ('gender', models.ForeignKey(blank=True, limit_choices_to={'type': 'gender'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='gender', to='hipeac.Metadata')),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profiles', to='hipeac.Institution')),
                ('meal_preference', models.ForeignKey(blank=True, limit_choices_to={'type': 'meal_preference'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_meal_preference', to='hipeac.Metadata')),
                ('position', models.ForeignKey(blank=True, limit_choices_to={'type': 'job_position'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_job_position', to='hipeac.Metadata')),
            ],
        ),
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('programme', models.CharField(blank=True, choices=[('FP7', 'FP7'), ('H2020', 'H2020')], max_length=5, null=True)),
                ('acronym', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=190)),
                ('description', models.TextField(blank=True, null=True, validators=[hipeac.validators.validate_no_badwords])),
                ('start_date', models.DateField(blank=True, null=True)),
                ('end_date', models.DateField(blank=True, null=True)),
                ('ec_project_id', models.PositiveIntegerField(blank=True, null=True, unique=True, verbose_name='Project ID')),
                ('image', models.FileField(blank=True, null=True, upload_to=hipeac.functions.get_images_path, verbose_name='Logo')),
                ('poster_file', models.FileField(blank=True, null=True, upload_to='raw/projects', verbose_name='Poster')),
                ('application_areas', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('topics', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('keywords', models.TextField(blank=True, editable=False, null=True)),
                ('updated_at', models.DateTimeField()),
                ('communication_officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='communicating_projects', to=settings.AUTH_USER_MODEL)),
                ('coordinating_institution', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coordinated_projects', to='hipeac.Institution')),
                ('coordinator', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coordinated_projects', to=settings.AUTH_USER_MODEL)),
                ('partners', models.ManyToManyField(blank=True, related_name='participated_projects', to='hipeac.Institution')),
                ('project_officer', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='officed_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['acronym'],
            },
            bases=(hipeac.models.mixins.ImagesMixin, hipeac.models.mixins.LinkMixin, hipeac.models.mixins.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(db_index=True)),
                ('title', models.TextField()),
                ('authors_string', models.TextField(verbose_name='Full authors string from DBLP')),
                ('dblp_key', models.CharField(max_length=200, unique=True)),
                ('url', models.URLField(blank=True, null=True, verbose_name='Electronic edition')),
                ('itemtype', models.CharField(blank=True, max_length=200, null=True)),
                ('authors', models.ManyToManyField(related_name='publications', to='hipeac.Profile')),
            ],
            options={
                'ordering': ('-year', 'title'),
            },
        ),
        migrations.CreateModel(
            name='PublicationConference',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('acronym', models.CharField(choices=[('ASPLOS', 'Conference on Architectural Support for Programming Languages and Operating Systems'), ('DAC', 'Design Automation Conference'), ('FCCM', 'Symposium on Field-Programmable Custom Computing Machines'), ('HPCA', 'International Symposium on High Performance Computer Architecture'), ('ISCA', 'International Symposium on Computer Architecture'), ('MICRO', 'Symposium on Microarchitecture'), ('PLDI', 'Conference on Programming Language Design and Implementation'), ('POPL', 'Symposium on Principles of Programming Languages')], max_length=16)),
                ('year', models.PositiveSmallIntegerField(db_index=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('url', models.URLField(verbose_name='DBLP event page')),
            ],
            options={
                'ordering': ('-year', 'acronym'),
            },
        ),
        migrations.CreateModel(
            name='PublicityEmail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('msgid', models.CharField(blank=True, max_length=1000, null=True)),
                ('date', models.CharField(blank=True, max_length=100, null=True)),
                ('subject', models.TextField()),
                ('content', models.TextField()),
                ('content_type', models.CharField(blank=True, max_length=190, null=True)),
                ('from_addresses', models.TextField(blank=True, null=True)),
                ('to_addresses', models.TextField(blank=True, null=True)),
                ('spam_level', models.PositiveSmallIntegerField(default=0)),
                ('keywords', models.TextField(blank=True, editable=False, null=True)),
            ],
            options={
                'db_table': 'hipeac_publicity_email',
            },
        ),
        migrations.CreateModel(
            name='Quote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(choices=[('general', 'General'), ('jobs', 'Jobs'), ('internships', 'PhD Internships'), ('industry', 'Industry'), ('innovation', 'Innovation community'), ('csw', 'Computing Systems Week'), ('conference', 'HiPEAC Conference'), ('acaces', 'ACACES'), ('roadshow', 'HiPEAC Roadshow'), ('collaborations', 'Collaboration Grants')], max_length=16)),
                ('text', models.TextField()),
                ('author', models.CharField(max_length=250)),
                ('is_featured', models.BooleanField(default=False)),
                ('institution', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotes', to='hipeac.Institution')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='quotes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Registration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False)),
                ('saldo', models.IntegerField(default=0)),
                ('invoice_requested', models.BooleanField(default=False)),
                ('invoice_sent', models.BooleanField(default=False)),
                ('visa_requested', models.BooleanField()),
                ('visa_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('coupon', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='hipeac.Coupon')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='registrations', to='hipeac.Event')),
                ('fee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to='hipeac.Fee')),
            ],
            options={
                'ordering': ('-created_at',),
            },
        ),
        migrations.CreateModel(
            name='RegistrationLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('registration', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='hipeac.Registration')),
            ],
        ),
        migrations.CreateModel(
            name='Roadshow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('name', models.CharField(max_length=250)),
                ('description', models.TextField(verbose_name='Presentation')),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('institutions', models.ManyToManyField(blank=True, help_text='Optionally, indicate institutions that will attend the event.', related_name='roadshow_events', to='hipeac.Institution')),
            ],
            options={
                'ordering': ['-start_date'],
            },
            bases=(hipeac.models.mixins.UrlMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Session',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_private', models.BooleanField(default=False)),
                ('date', models.DateField()),
                ('start_at', models.TimeField(blank=True, null=True)),
                ('end_at', models.TimeField(blank=True, null=True)),
                ('title', models.CharField(max_length=250)),
                ('summary', models.TextField(blank=True, null=True)),
                ('max_attendees', models.PositiveSmallIntegerField(default=0, help_text='Leave on `0` for non limiting.')),
                ('extra_attendees_fee', models.PositiveSmallIntegerField(default=0)),
                ('application_areas', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('topics', models.CharField(default='', max_length=250, validators=[django.core.validators.RegexValidator(re.compile('^\\d+(?:,\\d+)*\\Z'), code='invalid', message='Enter only digits separated by commas.')])),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sessions', to='hipeac.Event')),
                ('projects', models.ManyToManyField(related_name='sessions', to='hipeac.Project')),
            ],
            options={
                'ordering': ['date', 'start_at', 'end_at'],
            },
            bases=(hipeac.models.mixins.LinkMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='hipeac.Event')),
            ],
            options={
                'db_table': 'hipeac_event_track',
            },
        ),
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Vision',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=250)),
                ('description', models.TextField()),
                ('publication_date', models.DateField(default=django.utils.timezone.now)),
            ],
            options={
                'ordering': ['-publication_date'],
            },
        ),
        migrations.AddField(
            model_name='registrationlog',
            name='session',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='logs', to='hipeac.Session'),
        ),
        migrations.AddField(
            model_name='registration',
            name='sessions',
            field=models.ManyToManyField(related_name='registrations', to='hipeac.Session'),
        ),
        migrations.AddField(
            model_name='registration',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='registrations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='publication',
            name='conference',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='publications', to='hipeac.PublicationConference'),
        ),
        migrations.AddField(
            model_name='profile',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='profiles', to='hipeac.Project'),
        ),
        migrations.AddField(
            model_name='profile',
            name='second_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='second_profiles', to='hipeac.Institution'),
        ),
        migrations.AddField(
            model_name='profile',
            name='title',
            field=models.ForeignKey(blank=True, limit_choices_to={'type': 'title'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user_title', to='hipeac.Metadata'),
        ),
        migrations.AddField(
            model_name='permission',
            name='user',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='xpermissions', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddIndex(
            model_name='metadata',
            index=models.Index(fields=['type'], name='hipeac_meta_type_f3ab48_idx'),
        ),
        migrations.AddField(
            model_name='link',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='job',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_jobs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='job',
            name='employment_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'field': 'employment_type'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employment_type', to='hipeac.Metadata'),
        ),
        migrations.AddField(
            model_name='job',
            name='institution',
            field=models.ForeignKey(limit_choices_to={'country__in': ('BG', 'HR', 'CY', 'CZ', 'EE', 'HU', 'LV', 'LT', 'MT', 'PL', 'RO', 'SK', 'SI', 'AT', 'BE', 'DK', 'FI', 'FR', 'DE', 'GR', 'IE', 'IT', 'LU', 'NL', 'PT', 'ES', 'SE', 'GB', 'AL', 'AM', 'BA', 'FO', 'GE', 'IS', 'IL', 'MK', 'MD', 'ME', 'NO', 'RS', 'CH', 'TN', 'TR', 'UA')}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs', to='hipeac.Institution'),
        ),
        migrations.AddField(
            model_name='job',
            name='project',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jobs', to='hipeac.Project'),
        ),
        migrations.AddField(
            model_name='institution',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='children', to='hipeac.Institution'),
        ),
        migrations.AddField(
            model_name='image',
            name='content_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='contenttypes.ContentType'),
        ),
        migrations.AddField(
            model_name='fee',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fees', to='hipeac.Event'),
        ),
        migrations.AddField(
            model_name='event',
            name='coordinating_institution',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='coordinated_events', to='hipeac.Institution'),
        ),
        migrations.AddField(
            model_name='coupon',
            name='event',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to='hipeac.Event'),
        ),
        migrations.AddField(
            model_name='block',
            name='page',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='blocks', to='hipeac.Page'),
        ),
        migrations.AddField(
            model_name='article',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='authored_articles', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='article',
            name='event',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='articles', to='hipeac.Event'),
        ),
        migrations.AddField(
            model_name='article',
            name='institutions',
            field=models.ManyToManyField(blank=True, related_name='articles', to='hipeac.Institution'),
        ),
        migrations.AddField(
            model_name='article',
            name='projects',
            field=models.ManyToManyField(blank=True, related_name='articles', to='hipeac.Project'),
        ),
        migrations.AddIndex(
            model_name='session',
            index=models.Index(fields=['event', 'date'], name='hipeac_sess_event_i_aa2af2_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='registrationlog',
            unique_together={('registration', 'session')},
        ),
        migrations.AddIndex(
            model_name='registration',
            index=models.Index(fields=['uuid'], name='hipeac_regi_uuid_33aef4_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='registration',
            unique_together={('event', 'user')},
        ),
        migrations.AddIndex(
            model_name='quote',
            index=models.Index(fields=['type'], name='hipeac_quot_type_5be033_idx'),
        ),
        migrations.AddIndex(
            model_name='profile',
            index=models.Index(fields=['membership_tags'], name='hipeac_prof_members_7d3555_idx'),
        ),
        migrations.AddIndex(
            model_name='coupon',
            index=models.Index(fields=['code'], name='hipeac_coup_code_86749f_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='block',
            unique_together={('page', 'key')},
        ),
    ]
