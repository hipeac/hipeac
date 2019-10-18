import datetime

from allauth.socialaccount.providers.linkedin_oauth2.provider import LinkedInOAuth2Provider
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from typing import Any, Dict

from hipeac.models import Notification
from .generic import Notificator


class LinkedInNotificator(Notificator):
    category = 'linkedin_account'
    discard = True

    def deleteOne(self, *, user_id: int) -> None:
        Notification.objects.filter(category=self.category, user_id=user_id).delete()

    def process_data(self):
        self.delete()
        bulk_notifications = []
        deadline = timezone.now() + datetime.timedelta(days=1)

        with connection.cursor() as cursor:
            query = """
                SELECT u.id AS user_id
                FROM auth_user AS u
                INNER JOIN hipeac_profile AS p ON u.id = p.user_id
                WHERE u.id IN (
                    SELECT l.object_id
                    FROM hipeac_link AS l
                    WHERE l.content_type_id = 32 AND l.type = 'linkedin'
                ) AND u.id NOT IN (
                    SELECT s.user_id
                    FROM socialaccount_socialaccount AS s
                    WHERE s.provider = %s
                )
            """
            cursor.execute(query, [LinkedInOAuth2Provider.id])

            for result in cursor.fetchall():
                bulk_notifications.append((
                    self.category,  # category
                    result[0],  # user_id
                    result[0],  # object_id == user_id
                    self.to_json({  # data
                        'discard_id': result[0],
                    }),
                    deadline,  # deadline
                ))

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            'text': f'Connect your LinkedIn and HiPEAC accounts to be able to log in even if you change institutions.',
            'path': reverse('socialaccount_connections'),
        }


class MembershipIndustryNotificator(Notificator):
    category = 'membership_industry'
    discard = True

    def deleteOne(self, *, user_id: int) -> None:
        Notification.objects.filter(category=self.category, user_id=user_id).delete()

    def process_data(self):
        self.delete()
        bulk_notifications = []
        deadline = timezone.now() + datetime.timedelta(days=1)

        with connection.cursor() as cursor:
            query = """
                SELECT u.id AS user_id
                FROM auth_user AS u
                INNER JOIN hipeac_profile AS p ON u.id = p.user_id
                INNER JOIN hipeac_institution AS i ON p.institution_id = i.id
                WHERE i.type IN ('industry', 'sme')
                    AND p.membership_tags NOT LIKE '%member%'
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append((
                    self.category,  # category
                    result[0],  # user_id
                    result[0],  # object_id == user_id
                    self.to_json({  # data
                        'discard_id': result[0],
                    }),
                    deadline,  # deadline
                ))

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            'text': 'HiPEAC is always open to new members from industry. '
                    'HiPEAC membership is FREE and keeps you informed, supported and connected. '
                    'Become a Member now!',
            'path': '/network/#/benefits/industry/',
        }


class MembershipResearcherNotificator(Notificator):
    category = 'membership_researcher'
    discard = True

    def deleteOne(self, *, user_id: int) -> None:
        Notification.objects.filter(category=self.category, user_id=user_id).delete()

    def process_data(self):
        self.delete()
        bulk_notifications = []
        deadline = timezone.now() + datetime.timedelta(days=1)

        with connection.cursor() as cursor:
            query = """
                SELECT u.id AS user_id
                FROM auth_user AS u
                INNER JOIN hipeac_profile AS p ON u.id = p.user_id
                INNER JOIN hipeac_institution AS i ON p.institution_id = i.id
                INNER JOIN (
                    SELECT profile_id, count(id) AS publications
                    FROM hipeac_publication_authors
                    GROUP BY profile_id
                ) AS pub ON u.id = pub.profile_id
                WHERE i.type IN ('university', 'lab', 'innovation')
                    AND p.membership_tags NOT LIKE '%member%'
                    AND p.membership_tags NOT LIKE '%affiliate%'
                    AND pub.publications >= 50
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append((
                    self.category,  # category
                    result[0],  # user_id
                    result[0],  # object_id == user_id
                    self.to_json({  # data
                        'discard_id': result[0],
                    }),
                    deadline,  # deadline
                ))

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            'text': 'HiPEAC is always open to new members. '
                    'HiPEAC membership is FREE and keeps you informed, supported and connected. '
                    'Become a Member now!',
            'path': '/network/#/benefits/',
        }


class ResearchTopicsPendingNotificator(Notificator):
    category = 'research_topics_pending'
    discard = False

    def deleteOne(self, *, user_id: int) -> None:
        Notification.objects.filter(category=self.category, user_id=user_id).delete()

    def process_data(self):
        self.delete()
        bulk_notifications = []
        deadline = timezone.now() + datetime.timedelta(days=1)

        with connection.cursor() as cursor:
            query = """
                SELECT u.id AS user_id
                FROM auth_user AS u
                INNER JOIN hipeac_profile AS p ON u.id = p.user_id
                WHERE p.topics IS NULL OR p.topics = ''
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append((
                    self.category,  # category
                    result[0],  # user_id
                    result[0],  # object_id == user_id
                    '{}',  # data
                    deadline,  # deadline
                ))

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            'text': f'Include your **areas of expertise** in your research profile to help other researchers find you.',
            'path': f"{reverse('user_profile')}#/research/",
        }
