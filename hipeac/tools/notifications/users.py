import datetime

from allauth.socialaccount.providers.linkedin_oauth2.provider import LinkedInOAuth2Provider
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import pgettext_lazy, npgettext_lazy
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
