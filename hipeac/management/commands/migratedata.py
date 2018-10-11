import json
import pytz

from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.redirects.models import Redirect
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import connection
from django.template.defaultfilters import slugify
from django.utils import timezone
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session as OrmSession
from sqlalchemy import create_engine

from hipeac.models import (
    Image, Link, Metadata, Permission,
    Institution, Project, Profile,
    Job,
    Event, Session, Coupon, Fee, Registration, Poster,
    Roadshow,
    Article, Clipping, Quote, Vision
)


tz = pytz.timezone('Europe/Brussels')


class Command(BaseCommand):
    help = 'Creates mock data for all available models.'

    def automap_all_tables(self, uri):
        """http://docs.sqlalchemy.org/en/latest/orm/extensions/automap.html"""
        Base = automap_base()
        engine = create_engine(uri)
        Base.prepare(engine, reflect=True)

        return Base, OrmSession(engine)

    @staticmethod
    def batch(iterable, n=1):
        size = len(iterable)
        for ndx in range(0, size, n):
            yield iterable[ndx:min(ndx + n, size)]

    def out(self, msg_type: str, msg: str):
        if msg_type == 'info':
            return self.stdout.write(self.style.MIGRATE_HEADING(msg))
        if msg_type == 'success':
            return self.stdout.write(self.style.SUCCESS(msg))
        else:
            return self.stdout.write(msg)

    def handle(self, *args, **options):
        CONNECTION_URI = 'mysql://root@localhost:3306/hipeac4_dev'
        Base, session = self.automap_all_tables(CONNECTION_URI)

        # Update Site info

        self.out('info', 'Show must go on!')

        site = Site.objects.get(pk=1)
        site.domain = 'v5.hipeac.net'
        site.name = 'HiPEAC'
        site.save()

        # Related

        bulk_acl = []
        bulk_images = []
        bulk_links = []
        bulk_redirects = []

        # Metadatas

        PROFILE_CHOICES = [
            (Metadata.GENDER, {
                'F': 'Female',
                'M': 'Male',
            }),
            (Metadata.TITLE, {
                'MR': 'Mr.',
                'MRS': 'Mrs.',
                'DR': 'Dr.',
                'PROF': 'Prof.',
            }),
            (Metadata.MEAL_PREFERENCE, {
                'NORM': 'No special requirements',
                'VEGE': 'Vegetarian',
                'VEGA': 'Vegan',
                'KOSH': 'Kosher',
                'MUSL': 'Muslim',
                'INGL': '[Intolerant] Gluten',
                'INLA': '[Intolerant] Lactose',
                'ALCR': '[Allergic] Crustaceans',
                'ALPE': '[Allergic] Peanuts',
            }),
            (Metadata.EMPLOYMENT, {
                'FULL': 'Full-time',
                'INTERN': 'Internship',
            }),
        ]

        CHOICES_DICT = {
            Metadata.GENDER: {},
            Metadata.TITLE: {},
            Metadata.MEAL_PREFERENCE: {},
            Metadata.EMPLOYMENT: {},
        }

        for choice in PROFILE_CHOICES:
            for item in choice[1].items():
                CHOICES_DICT[choice[0]][item[0]] = Metadata.objects.create(
                    type=choice[0],
                    value=item[1],
                )

        # Positions
        JOB_POSITIONS_DICT = {}
        for profile in session.query(Base.classes.core_profile).all():
            JOB_POSITIONS_DICT[profile.id] = Metadata.objects.create(
                type=Metadata.JOB_POSITION,
                value=profile.name,
                position=profile.order,
            )

        # Application areas
        AREAS_DICT = {}
        for area in session.query(Base.classes.core_applicationarea).all():
            AREAS_DICT[area.id] = Metadata.objects.create(
                type=Metadata.APPLICATION_AREA,
                value=area.name,
                position=area.id,
            )

        # Topics
        TOPICS_DICT = {}
        for topic in session.query(Base.classes.core_topic).all():
            TOPICS_DICT[topic.id] = Metadata.objects.create(
                type=Metadata.TOPIC,
                value=topic.name,
                position=topic.id,
            )

        # Institutions

        self.out('std', 'Migrating institutions...')
        bulk_institutions = []
        institution_countries = {}
        ct = ContentType.objects.get_for_model(Institution)

        institution_types = {
            'UNI': Institution.UNIVERSITY,
            'LAB': Institution.LAB,
            'INN': Institution.INNOVATION,
            'COM': Institution.INDUSTRY,
            'SME': Institution.SME,
            'OTH': Institution.OTHER,
        }

        for inst in session.query(Base.classes.core_institution).all():
            institution_countries[inst.id] = inst.country
            bulk_institutions.append(Institution(
                id=inst.id,
                name=inst.name,
                local_name=inst.local_name,
                colloquial_name=inst.colloquial_name,
                type=institution_types[inst.institution_type],
                location=inst.city,
                country=inst.country,
                description=inst.description,
                recruitment_contact=inst.recruitment_contact,
                recruitment_email=inst.recruitment_email,
                image=inst.image if inst.image else None,
                updated_at=tz.localize(inst.created_at).astimezone(pytz.utc),
            ))
            if inst.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=inst.id,
                    type=Link.WEBSITE,
                    url=inst.url
                ))
            if inst.recruitment_url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=inst.id,
                    type=Link.OTHER,
                    url=inst.recruitment_url
                ))
            if inst.twitter:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=inst.id,
                    type=Link.TWITTER,
                    url=f'https://twitter.com/{inst.twitter}'
                ))

        Institution.objects.bulk_create(bulk_institutions, batch_size=1000)

        for inst in session.query(Base.classes.core_institution).all():
            if inst.parent_id:
                i = Institution.objects.get(id=inst.id)
                i.parent_id = inst.parent_id
                i.save()

        self.out('success', f'✔ Institutions migrated! ({len(bulk_institutions)} records)')

        # Users

        self.out('std', 'Migrating user profiles...')
        bulk_users = []
        bulk_profiles = []
        ct = ContentType.objects.get_for_model(Profile)
        cti = ContentType.objects.get_for_model(Institution)

        for u in session.query(Base.classes.core_user).all():

            membership_tags = []
            if u.membership_type == 'MEMB':
                membership_tags.append('member-eu')
            if u.membership_type == 'ASSO':
                membership_tags.append('member-non-eu')
            if u.membership_type in ['AFFI', 'APHD', 'STAF']:
                membership_tags.append('affiliated')
            if u.membership_type == 'APHD':
                membership_tags.append('phd')
            if u.membership_type == 'STAF':
                membership_tags.append('staff')
            if u.is_innovation:
                membership_tags.append('innovation')
            if u.membership_type and u.gender:
                membership_tags.append('female' if u.gender == 'F' else 'male')

            title = 'MR' if u.title == 'M~R' else u.title
            meal_preference = CHOICES_DICT[Metadata.MEAL_PREFERENCE][u.meal_preference] if u.meal_preference else None
            bulk_users.append(User(
                id=u.id,
                username=u.username,
                email=u.email.lower() if u.email else None,
                password=u.password,
                first_name=u.first_name,
                last_name=u.last_name,
                last_login=tz.localize(u.last_login).astimezone(pytz.utc) if u.last_login else None,
                is_superuser=u.is_superuser,
                is_staff=u.is_staff,
                is_active=u.is_active if not u.is_retired else False,
                date_joined=tz.localize(u.date_joined).astimezone(pytz.utc),
            ))
            bulk_profiles.append(Profile(
                user_id=u.id,
                gender=CHOICES_DICT[Metadata.GENDER][u.gender] if u.gender else None,
                title=CHOICES_DICT[Metadata.TITLE][title] if title else None,
                meal_preference=meal_preference,
                country=u.country,
                position=JOB_POSITIONS_DICT[u.profile_id] if u.profile_id else None,
                department=u.department,
                institution_id=u.institution_id if u.institution_id != 916 else None,  # hack
                second_institution_id=u.second_institution_id if u.second_institution_id != 2979 else None,  # hack
                bio=u.bio,
                is_bouncing=False,
                is_subscribed=u.is_subscribed,
                is_public=u.is_public,
                membership_tags=','.join(sorted(membership_tags)),
                membership_date=u.membership_date,
                membership_revocation_date=u.membership_revocation_date,
                advisor_id=u.advisor_id,
            ))
            if u.membership_type in ['MEMB', 'ASSO'] and u.institution_id:
                bulk_acl.append(Permission(
                    content_type=cti,
                    object_id=u.institution_id,
                    user_id=u.id,
                    level=Permission.ADMIN,
                ))
            if u.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=u.id,
                    type=Link.WEBSITE,
                    url=u.url
                ))
            if u.url_dblp:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=u.id,
                    type=Link.DBLP if 'dblp' in u.url_dblp else Link.OTHER,
                    url=u.url_dblp
                ))
            if u.twitter:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=u.id,
                    type=Link.TWITTER,
                    url=f'https://twitter.com/{u.twitter}'
                ))
            if u.url_cv:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=u.id,
                    type=Link.LINKEDIN if 'linkedin' in u.url_cv else Link.OTHER,
                    url=u.url_cv
                ))

        User.objects.bulk_create(bulk_users, batch_size=1000)
        Profile.objects.bulk_create(bulk_profiles, batch_size=1000)
        self.out('success', f'✔ User profiles migrated! ({len(bulk_users)} records)')

        # Projects

        self.out('std', 'Migrating related projects...')
        bulk_projects = []
        project_topics = {}
        ct = ContentType.objects.get_for_model(Project)

        for t in session.query(Base.classes.core_project_topics).all():
            if t.project_id not in project_topics:
                project_topics[t.project_id] = []
            project_topics[t.project_id].append(str(TOPICS_DICT[t.topic_id].id))

        for pr in session.query(Base.classes.core_project).all():
            bulk_projects.append(Project(
                id=pr.id,
                acronym=pr.acronym,
                name=pr.name,
                description=pr.description,
                programme=pr.programme,
                coordinator_id=pr.coordinator_id,
                coordinating_institution_id=pr.coordinating_institution_id,
                project_officer_id=pr.project_officer_id,
                communication_officer_id=pr.communication_officer_id,
                ec_project_id=pr.ec_project_id,
                start_date=pr.start_date,
                end_date=pr.end_date,
                image=pr.image if pr.image else None,
                updated_at=tz.localize(pr.created_at).astimezone(pytz.utc),
                keywords=json.dumps([]),
                topics=','.join(project_topics[pr.id]) if pr.id in project_topics else '',
            ))
            for user_id in [uid for uid in [pr.coordinator_id, pr.communication_officer_id] if uid]:
                bulk_acl.append(Permission(
                    content_type=ct,
                    object_id=pr.id,
                    user_id=user_id,
                    level=Permission.ADMIN,
                ))
            if pr.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=pr.id,
                    type=Link.WEBSITE,
                    url=pr.url
                ))
            if pr.twitter:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=pr.id,
                    type=Link.TWITTER,
                    url=f'https://twitter.com/{pr.twitter}'
                ))
            if pr.twitter:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=pr.id,
                    type=Link.OTHER,
                    url=f'http://cordis.europa.eu/project/rcn/{pr.cordis_record_number}_en.html'
                ))
            if pr.youtube_id:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=pr.id,
                    type=Link.YOUTUBE,
                    url=f'https://youtu.be/{pr.youtube_id}'
                ))

        Project.objects.bulk_create(bulk_projects, batch_size=1000)
        self.out('success', f'✔ Projects migrated! ({len(bulk_projects)} records)')

        bulk_project_partners = []
        for rel in session.query(Base.classes.core_project_partners).yield_per(10000):
            bulk_project_partners.append((
                rel.id,
                rel.project_id,
                rel.institution_id,
            ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_project_partners, 10000):
                query = """
                    INSERT INTO hipeac_project_partners (id, project_id, institution_id)
                    VALUES (%s, %s, %s)
                """
                cursor.executemany(query, batch)

        self.out('success', '✔ Partners added to projects!')

        bulk_profile_projects = []
        for rel in session.query(Base.classes.core_user_projects).yield_per(10000):
            bulk_profile_projects.append((
                rel.id,
                rel.user_id,
                rel.project_id,
            ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_profile_projects, 10000):
                query = """
                    INSERT INTO hipeac_profile_projects (id, profile_id, project_id)
                    VALUES (%s, %s, %s)
                """
                cursor.executemany(query, batch)

        self.out('success', '✔ Projects added to users!')

        # HiPEAC

        hipeac_ids = {
            # 1: 1,  # new
            # 2: 2,  # new
            3: 6750,
            4: 6828,
            5: 6907,
        }

        for p in session.query(Base.classes.core_hipeac_steering_committee).all():
            if p.hipeac_id in hipeac_ids:
                bulk_acl.append(Permission(
                    content_type=ct,
                    object_id=hipeac_ids[p.hipeac_id],
                    user_id=p.user_id,
                    level=Permission.ADMIN,
                ))

        for p in session.query(Base.classes.core_hipeac_granted_users).all():
            if p.hipeac_id in hipeac_ids:
                bulk_acl.append(Permission(
                    content_type=ct,
                    object_id=hipeac_ids[p.hipeac_id],
                    user_id=p.user_id,
                    level=Permission.GUEST,
                ))

        self.out('success', '✔ HiPEAC project permissions migrated!')

        # Publications

        self.out('std', 'Migrating publications...')
        from hipeac.models import PublicationConference

        conference_ids = {
            1: 'DAC',
            2: 'POPL',
            3: 'PLDI',
            4: 'ASPLOS',
            5: 'ISCA',
            6: 'HPCA',
            7: 'MICRO',
            8: 'FCCM',
        }

        for conf in session.query(Base.classes.research_event).all():
            if p.hipeac_id in hipeac_ids:
                PublicationConference.objects.create(
                    id=conf.id,
                    acronym=conference_ids[conf.conference_id],
                    year=conf.year,
                    country=conf.country,
                    url=conf.url,
                )

        bulk_publications = []
        for pub in session.query(Base.classes.research_publication).yield_per(10000):
            bulk_publications.append((
                pub.id,
                pub.year,
                pub.title,
                pub.authors_string,
                pub.dblp_key,
                pub.url,
                pub.itemtype,
                pub.event_id,
            ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_publications, 10000):
                query = """
                    INSERT INTO hipeac_publication (
                        id, year, title, authors_string, dblp_key, url, itemtype, conference_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.executemany(query, batch)

        bulk_publication_authors = []
        for rel in session.query(Base.classes.research_publication_authors).yield_per(10000):
            bulk_publication_authors.append((
                rel.id,
                rel.publication_id,
                rel.user_id,
            ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_publication_authors, 10000):
                query = """
                    INSERT INTO hipeac_publication_authors (id, publication_id, profile_id)
                    VALUES (%s, %s, %s)
                """
                cursor.executemany(query, batch)

        self.out('success', f'✔ Publications migrated! ({len(bulk_publications)} records)')

        # Jobs

        self.out('std', 'Migrating jobs...')
        bulk_jobs = []
        bulk_job_profiles = []
        job_topics = {}
        job_career_levels = {}
        ct = ContentType.objects.get_for_model(Job)

        for t in session.query(Base.classes.jobs_job_topics).all():
            if t.job_id not in job_topics:
                job_topics[t.job_id] = []
            job_topics[t.job_id].append(str(TOPICS_DICT[t.topic_id].id))

        for p in session.query(Base.classes.jobs_job_profiles).all():
            if p.job_id not in job_career_levels:
                job_career_levels[p.job_id] = []
            job_career_levels[p.job_id].append(str(JOB_POSITIONS_DICT[p.profile_id].id))

        for job in session.query(Base.classes.jobs_job).all():
            emp = 'INTERN' if job.is_internship else 'FULL'
            bulk_jobs.append(Job(
                id=job.id,
                title=job.title,
                description=job.description,
                deadline=job.deadline,
                positions=job.positions,
                country=institution_countries[job.institution_id] if job.institution_id else None,
                email=job.email.lower() if job.email else None,
                share=job.share,
                reminded_deadline=job.reminder_sent_for,
                created_at=tz.localize(job.created_at).astimezone(pytz.utc),
                updated_at=tz.localize(job.created_at).astimezone(pytz.utc),
                institution_id=job.institution_id,
                project_id=job.project_id,
                employment_type=CHOICES_DICT[Metadata.EMPLOYMENT][emp],
                keywords=json.dumps([]),
                topics=','.join(job_topics[job.id]) if job.id in job_topics else '',
                career_levels=','.join(job_career_levels[job.id]) if job.id in job_career_levels else '',
                created_by_id=job.created_by_id,
            ))
            if job.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=job.id,
                    type=Link.WEBSITE,
                    url=job.url
                ))

        Job.objects.bulk_create(bulk_jobs, batch_size=1000)
        self.out('success', f'✔ Jobs migrated! ({len(bulk_jobs)} records)')

        # Events

        self.out('std', 'Migrating events...')
        bulk_events = []
        ct = ContentType.objects.get_for_model(Event)

        confs = {}
        for c in session.query(Base.classes.conferences_conference).all():
            confs[c.event_ptr_id] = c

        event_types = {
            'ACACES': Event.ACACES,
            'CONF': Event.CONFERENCE,
            'CSW': Event.CSW,
            'ECMEET': Event.EC_MEETING,
        }

        for ev in session.query(Base.classes.events_event).all():
            t = datetime.min.time()
            tz_dead = tz.localize(datetime.combine(ev.registration_deadline, t)).astimezone(pytz.utc)
            if ev.id in confs and confs[ev.id].early_registration_deadline:
                tz_ear = tz.localize(datetime.combine(confs[ev.id].early_registration_deadline, t)).astimezone(pytz.utc)
            else:
                tz_ear = None
            bulk_events.append(Event(
                id=ev.id,
                type=event_types[ev.event_type],
                coordinating_institution_id=237 if ev.event_type == 'ACACES' else ev.coordinator_id,
                city=ev.city,
                slug=slugify(ev.city),
                country=ev.country,
                hashtag=ev.hashtag,
                start_date=ev.start_date,
                end_date=ev.end_date,
                registration_start_date=ev.registration_start_date,
                registration_early_deadline=tz_ear,
                registration_deadline=ev.end_date if ev.registration_deadline == '1970-01-01' else tz_dead,
                travel_info=ev.travel_information,
            ))
            if ev.google_album_url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=ev.id,
                    type=Link.GOOGLE_PHOTOS,
                    url=ev.google_album_url
                ))
            if ev.google_mid:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=ev.id,
                    type=Link.GOOGLE_MAPS,
                    url=f'https://drive.google.com/open?id={ev.google_mid}&usp=sharing'
                ))

        Event.objects.bulk_create(bulk_events, batch_size=1000)
        self.out('success', f'✔ Events migrated! ({len(bulk_events)} records)')

        # Sessions

        event_urls = {e.id: e.get_absolute_url() for e in Event.objects.all()}

        self.out('std', 'Migrating event sessions...')
        bulk_sessions = []
        session_areas = {}
        session_topics = {}
        session_ids = []
        ct = ContentType.objects.get_for_model(Session)

        for a in session.query(Base.classes.events_activity_areas).all():
            if a.activity_id not in session_areas:
                session_areas[a.activity_id] = []
            session_areas[a.activity_id].append(str(AREAS_DICT[a.applicationarea_id].id))

        for t in session.query(Base.classes.events_activity_topics).all():
            if t.activity_id not in session_topics:
                session_topics[t.activity_id] = []
            session_topics[t.activity_id].append(str(TOPICS_DICT[t.topic_id].id))

        for s in session.query(Base.classes.events_activity).all():
            if s.event_id is None:
                continue

            session_ids.append(s.id)
            bulk_sessions.append(Session(
                id=s.id,
                event_id=s.event_id,
                date=s.date if s.date else '2016-04-27',
                start_at=s.start_at,
                end_at=s.end_at,
                title=s.title,
                summary=s.description,
                max_attendees=s.max_attendants,
                extra_attendees_fee=s.extra_price,
                is_private=s.is_private,
                application_areas=','.join(session_areas[s.id]) if s.id in session_areas else '',
                topics=','.join(session_topics[s.id]) if s.id in session_topics else '',
                created_at=timezone.now(),
                updated_at=timezone.now(),
            ))
            if s.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=s.id,
                    type=Link.WEBSITE,
                    url=s.url
                ))
            if s.youtube_id:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=s.id,
                    type=Link.YOUTUBE,
                    url=f'https://youtu.be/{s.youtube_id}' if 'user' not in s.youtube_id else s.youtube_id
                ))

            bulk_redirects.append(Redirect(
                site_id=1,
                old_path=f'/events/activities/{s.id}/{s.slug}/',
                new_path=f'{event_urls[s.event_id]}#/programme/{s.id}/',
            ))

        for org in session.query(Base.classes.events_activity_organizers).all():
            bulk_acl.append(Permission(
                content_type=ct,
                object_id=org.activity_id,
                user_id=org.user_id,
                level=Permission.ADMIN,
            ))

        Session.objects.bulk_create(bulk_sessions, batch_size=1000)
        self.out('success', f'✔ Sessions migrated! ({len(bulk_sessions)} records)')

        # Coupons

        self.out('std', 'Migrating coupons...')
        bulk_coupons = []

        for coupon in session.query(Base.classes.conferences_coupon).all():
            bulk_coupons.append(Coupon(
                id=coupon.id,
                event_id=coupon.conference_id,
                value=coupon.value,
                notes=coupon.description,
                created_at=tz.localize(coupon.created_at, is_dst=None).astimezone(pytz.utc),
            ))

        Coupon.objects.bulk_create(bulk_coupons, batch_size=1000)
        self.out('success', f'✔ Coupons migrated! ({len(bulk_coupons)} records)')

        # Fees

        self.out('std', 'Migrating fees...')
        bulk_fees = []

        for conf in session.query(Base.classes.conferences_conference).all():
            if conf.fee == 0:
                continue
            bulk_fees.append(Fee(
                event_id=conf.event_ptr_id,
                type=Fee.EARLY,
                value=conf.early_registration_fee,
            ))
            bulk_fees.append(Fee(
                event_id=conf.event_ptr_id,
                type=Fee.LATE,
                value=conf.fee,
            ))
            bulk_fees.append(Fee(
                event_id=conf.event_ptr_id,
                type=Fee.EARLY_STUDENT,
                value=conf.early_registration_student_fee,
            ))
            bulk_fees.append(Fee(
                event_id=conf.event_ptr_id,
                type=Fee.LATE_STUDENT,
                value=conf.student_fee,
            ))
            bulk_fees.append(Fee(
                event_id=conf.event_ptr_id,
                type=Fee.BOOTH,
                value=conf.booth_rent_fee,
            ))

        Fee.objects.bulk_create(bulk_fees, batch_size=1000)
        self.out('success', f'✔ Fees migrated! ({len(bulk_fees)} records)')

        fees_dict = {}
        for fee in Fee.objects.all():
            fees_dict[(fee.event_id, fee.value)] = fee

        # Registrations

        self.out('std', 'Migrating registrations...')
        registrations = {}
        bulk_registrations = []

        for reg in session.query(Base.classes.events_registration).all():
            registrations[reg.id] = Registration(
                id=reg.id,
                event_id=reg.event_id,
                user_id=reg.user_id,
                invoice_requested=False,
                visa_requested=reg.with_visa,
                created_at=tz.localize(reg.created_at, is_dst=None).astimezone(pytz.utc),
                updated_at=tz.localize(reg.created_at, is_dst=None).astimezone(pytz.utc),
            )

        for reg in session.query(Base.classes.conferences_registration).all():
            r = registrations[reg.registration_ptr_id]
            r.coupon_id = reg.coupon_id
            r.invoice_requested = reg.with_invoice
            r.invoice_sent = reg.invoice_sent
            r.saldo = reg.saldo

            try:
                r.fee_id = fees_dict[(r.event_id, reg.base_fee)].id
            except Exception as e:
                pass

        bulk_registrations = list(registrations.values())
        Registration.objects.bulk_create(bulk_registrations, batch_size=1000)
        self.out('success', f'✔ Registrations migrated! ({len(bulk_registrations)} records)')

        registration_ids = list(registrations.keys())

        bulk_session_regs = []
        for rel in session.query(Base.classes.events_attendance).yield_per(10000):
            if rel.registration_id in registration_ids and rel.activity_id in session_ids:
                bulk_session_regs.append((
                    rel.id,
                    rel.registration_id,
                    rel.activity_id,
                ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_session_regs, 10000):
                query = """
                    INSERT INTO hipeac_registration_sessions (id, registration_id, session_id)
                    VALUES (%s, %s, %s)
                """
                cursor.executemany(query, batch)

        bulk_session_logs = []
        for rel in session.query(Base.classes.events_attendance_cache).yield_per(10000):
            if rel.registration_id in registration_ids and rel.activity_id in session_ids:
                bulk_session_logs.append((
                    rel.id,
                    rel.registration_id,
                    rel.activity_id,
                    tz.localize(rel.created_at).astimezone(pytz.utc),
                ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_session_logs, 10000):
                query = """
                    INSERT INTO hipeac_registrationlog (id, registration_id, session_id, created_at)
                    VALUES (%s, %s, %s, %s)
                """
                cursor.executemany(query, batch)

        self.out('success', '✔ Session registrations migrated!')

        # Update posters

        for reg in session.query(Base.classes.conferences_registration).all():
            if reg.registration_ptr_id in registration_ids:
                if reg.poster and reg.poster != '0':
                    Poster.objects.create(
                        registration_id=reg.registration_ptr_id,
                        title=reg.poster if reg.poster != '1' else '(untitled)',
                        type=Poster.STUDENT,
                    )

                if reg.poster_eu_project and reg.poster_eu_project != '':
                    Poster.objects.create(
                        registration_id=reg.registration_ptr_id,
                        title=reg.poster_eu_project,
                        type=Poster.PROJECT,
                    )

                if reg.poster_industrial and reg.poster_industrial != '':
                    Poster.objects.create(
                        registration_id=reg.registration_ptr_id,
                        title=reg.poster_industrial,
                        type=Poster.INDUSTRY,
                    )

        self.out('success', '✔ Posters migrated!')

        # Update counters

        for event in Event.objects.all():
            event.registrations_count = event.registrations.count()
            event.save()

        # Roadshows

        self.out('std', 'Migrating Roadshows...')
        bulk_roadshows = []
        ct = ContentType.objects.get_for_model(Roadshow)

        for ro in session.query(Base.classes.roadshow_event).all():
            bulk_roadshows.append(Roadshow(
                id=ro.id,
                name=ro.name,
                description=ro.description,
                start_date=ro.start_date,
                end_date=ro.end_date,
                country=ro.country
            ))

            if ro.url:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=ro.id,
                    type=Link.WEBSITE,
                    url=ro.url
                ))
            if ro.twitter:
                bulk_links.append(Link(
                    content_type=ct,
                    object_id=ro.id,
                    type=Link.TWITTER,
                    url=f'https://twitter.com/{ro.twitter}'
                ))

        Roadshow.objects.bulk_create(bulk_roadshows, batch_size=1000)

        bulk_roadshow_institutions = []
        for rel in session.query(Base.classes.roadshow_event_institutions).yield_per(10000):
            bulk_roadshow_institutions.append((
                rel.id,
                rel.event_id,
                rel.institution_id,
            ))

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_roadshow_institutions, 10000):
                query = """
                    INSERT INTO hipeac_roadshow_institutions (id, roadshow_id, institution_id)
                    VALUES (%s, %s, %s)
                """
                cursor.executemany(query, batch)

        self.out('success', f'✔ Roadshows migrated! ({len(bulk_roadshows)} records)')

        # Vision

        self.out('std', 'Migrating Vision...')
        bulk_visions = []
        ct = ContentType.objects.get_for_model(Vision)

        for v in session.query(Base.classes.publications_vision).all():
            bulk_visions.append(Vision(
                id=v.id,
                title=v.title,
                introduction=v.description,
                summary=v.summary,
                publication_date=v.release_date,
                file=v.file,
                file_draft=v.file_draft,
                downloads=v.downloads,
                downloads_draft=v.draft_downloads,
            ))

            bulk_images.append(Image(
                content_type=ct,
                object_id=v.id,
                image=v.image,
            ))

            bulk_links.append(Link(
                content_type=ct,
                object_id=v.id,
                type=Link.YOUTUBE,
                url=f'https://www.youtube.com/watch?v={v.youtube_id}'
            ))

        Vision.objects.bulk_create(bulk_visions, batch_size=1000)
        self.out('success', f'✔ Vision migrated! ({len(bulk_visions)} records)')

        # Articles

        self.out('std', 'Migrating articles...')
        bulk_articles = []
        ct = ContentType.objects.get_for_model(Article)

        for article in session.query(Base.classes.press_article).all():
            bulk_articles.append(Article(
                id=article.id,
                type=article.type.lower(),
                publication_date=article.release_date,
                title=article.title,
                excerpt=article.excerpt,
                content=article.body,
                is_ready=(article.status == 'OK'),
                created_at=tz.localize(article.created_at, is_dst=None).astimezone(pytz.utc),
                created_by_id=article.author_id
            ))

        for art_photo in session.query(Base.classes.press_article_photos).all():
            bulk_images.append(Image(
                content_type=ct,
                object_id=art_photo.article_id,
                image=art_photo.file,
                position=art_photo.position,
            ))

        Article.objects.bulk_create(bulk_articles, batch_size=1000)
        self.out('success', f'✔ Articles migrated! ({len(bulk_articles)} records)')

        # Clippings

        self.out('std', 'Migrating clippings...')
        bulk_clippings = []

        for clip in session.query(Base.classes.press_clip).all():
            bulk_clippings.append(Clipping(
                id=clip.id,
                media=clip.media,
                title=clip.title,
                url=clip.url,
                publication_date=clip.published_at,
            ))

        Clipping.objects.bulk_create(bulk_clippings, batch_size=1000)
        self.out('success', f'✔ Clippings migrated! ({len(bulk_clippings)} records)')

        # Quotes

        self.out('std', 'Migrating quotes...')
        bulk_quotes = []

        quote_types = {
            'GEN': 'network',
            'JOBS': 'jobs',
            'COLL': 'collaborations',
            'INTE': 'internships',
            'CSW': 'csw',
            'COM': 'industry',
            'CONF': 'conference',
            'ROAD': 'roadshow',
            'ACAC': 'acaces',
        }

        for quote in session.query(Base.classes.quotes_quote).all():
            bulk_quotes.append(Quote(
                id=quote.id,
                user_id=quote.user_id,
                institution_id=quote.institution_id,
                is_featured=quote.is_featured,
                text=quote.text,
                author=quote.author,
                type=quote_types[quote.type]
            ))

        Quote.objects.bulk_create(bulk_quotes, batch_size=1000)
        self.out('success', f'✔ Quotes migrated! ({len(bulk_quotes)} records)')

        # Save permissions and links

        Permission.objects.bulk_create(bulk_acl, batch_size=1000)
        Link.objects.bulk_create(bulk_links, batch_size=1000)
        Image.objects.bulk_create(bulk_images, batch_size=1000)

        with connection.cursor() as cursor:
            for batch in self.batch(bulk_job_profiles, 10000):
                query = """
                    INSERT INTO hipeac_job_career_levels (job_id, metadata_id)
                    VALUES (%s, %s)
                """
                cursor.executemany(query, batch)

        # Cleanup

        for link in Link.objects.all():
            if 'github.com' in link.url:
                link.type = link.GITHUB
                link.save()
            if 'easychair.org' in link.url:
                link.type = link.EASYCHAIR
                link.save()

        other = Metadata.objects.get(value='_Other_')
        other.value = 'Other'
        other.position = 99
        other.save()

        # Redirects

        """
        hipeac.net/vision
        hipeac.net/join
        hipeac.net/conference
        hipeac.net/industry
        """

        self.out('std', 'Updating redirects...')
        redirects = (
            ('/acaces/', '/events/#/acaces/'),
            ('/csw/', '/events/#/csw/'),
            ('/conferences/', '/events/#/conference/'),
            ('/about/', '/network/#/'),
            ('/about/contact/', '/network/#/'),
            ('/industry/', '/network/#/industry/'),
            ('/members/', '/network/#/members/'),
            ('/members/stakeholders/', '/network/#/stakeholders/'),
            ('/members/membership/', '/network/#/membership/'),
            ('/membership/', '/network/#/membership/'),
            ('/stakeholders/', '/network/#/stakeholders/'),
            ('/network/projects/', '/network/#/projects/'),
            ('/projects/', '/network/#/projects/'),
            ('/partners/', '/network/#/partners/'),
            ('/jobs/about/', '/jobs/#/recruitment/'),
            ('/press/blog/', '/news/#/blog/'),
            ('/press/news/', '/news/#/archive/'),
            ('/press/clippings/', '/press/#/clippings/'),
            ('/press/releases/', '/press/#/releases/'),
            ('/press/quotes/', '/press/#/'),
            ('/publications/newsletter/', '/news/#/magazine/'),
            ('/publications/vision/', '/vision/#/'),
            ('/jobs/career-center/', '/jobs/#/career-center/'),
            ('/cloud/', 'https://cloud.hipeac.net/'),
            ('/linkedin/', 'https://www.linkedin.com/company/hipeac/'),
            ('/twitter/', 'https://twitter.com/hipeac'),
            ('/research/paper-awards/', '/research/#/paper-awards/'),
        )

        for r in redirects:
            bulk_redirects.append(Redirect(
                site_id=1,
                old_path=r[0],
                new_path=r[1],
            ))

        Redirect.objects.bulk_create(bulk_redirects)
        self.out('success', f'✔ Redirects created! ({len(bulk_redirects)} records)')
