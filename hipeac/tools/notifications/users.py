import datetime

from allauth.socialaccount.providers.linkedin_oauth2.provider import LinkedInOAuth2Provider
from django.db import connection
from django.urls import reverse
from django.utils import timezone
from typing import Any, Dict

from hipeac.models import Notification
from .generic import Notificator


class LinkedInNotificator(Notificator):
    category = "linkedin_account"
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
                    FROM hipeac_rel_link AS l
                    WHERE l.content_type_id = 48 AND l.type = 'linkedin'
                ) AND u.id NOT IN (
                    SELECT s.user_id
                    FROM socialaccount_socialaccount AS s
                    WHERE s.provider = %s
                )
            """
            cursor.execute(query, [LinkedInOAuth2Provider.id])

            for result in cursor.fetchall():
                bulk_notifications.append(
                    (
                        self.category,  # category
                        result[0],  # user_id
                        result[0],  # object_id == user_id
                        self.to_json({"discard_id": result[0]}),  # data
                        deadline,  # deadline
                    )
                )

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            "text": "Connect your LinkedIn and HiPEAC accounts to be able to log in even if you change institutions.",
            "path": reverse("socialaccount_connections"),
        }


class MembershipIndustryNotificator(Notificator):
    category = "membership_industry"
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
                    AND u.id NOT IN (SELECT user_id FROM hipeac_membership_member)
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append(
                    (
                        self.category,  # category
                        result[0],  # user_id
                        result[0],  # object_id == user_id
                        self.to_json({"discard_id": result[0]}),  # data
                        deadline,  # deadline
                    )
                )

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            "text": "HiPEAC is always open to new members from industry. "
            "HiPEAC membership is FREE and keeps you informed, supported and connected. "
            "Become a Member now!",
            "path": "/network/#/benefits/industry/",
        }


class MembershipResearcherNotificator(Notificator):
    category = "membership_researcher"
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
                    SELECT user_id, count(id) AS publications
                    FROM hipeac_rel_user
                    WHERE user_id NOT IN (SELECT user_id FROM hipeac_membership_member)
                        AND content_type_id = 50
                    GROUP BY user_id
                ) AS pub ON u.id = pub.user_id
                INNER JOIN (
                    SELECT rel.user_id, count(rel.id) AS publications
                    FROM hipeac_rel_user AS rel
                    INNER JOIN hipeac_publication AS p ON rel.object_id = p.id
                    WHERE rel.user_id NOT IN (SELECT user_id FROM hipeac_membership_member)
                    	AND content_type_id = 50 AND p.conference_id IS NOT NULL
                    GROUP BY user_id
                ) AS awards ON u.id = pub.user_id
                WHERE i.type IN ('university', 'lab', 'innovation')
                    AND u.id NOT IN (SELECT user_id FROM hipeac_membership_member)
                    AND (pub.publications >= 50 OR awards.publications >= 1)
                GROUP BY u.id;
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append(
                    (
                        self.category,  # category
                        result[0],  # user_id
                        result[0],  # object_id == user_id
                        self.to_json({"discard_id": result[0]}),  # data
                        deadline,  # deadline
                    )
                )

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            "text": "HiPEAC is always open to new members. "
            "HiPEAC membership is FREE and keeps you informed, supported and connected. "
            "Become a Member now!",
            "path": "/network/#/benefits/",
        }


class ResearchTopicsPendingNotificator(Notificator):
    category = "research_topics_pending"
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
                WHERE u.id NOT IN (
                    SELECT object_id
                    FROM hipeac_rel_topic
                    WHERE content_type_id = 48
                )
            """
            cursor.execute(query)

            for result in cursor.fetchall():
                bulk_notifications.append(
                    (
                        self.category,  # category
                        result[0],  # user_id
                        result[0],  # object_id == user_id
                        "{}",  # data
                        deadline,  # deadline
                    )
                )

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        return {
            "text": "Include your **areas of expertise** in your research profile to help other researchers find you.",
            "path": f"{reverse('user_profile')}#/research/",
        }
