import json

from django.db import connection
from typing import Any, Dict, List, Tuple

from hipeac.models import Notification


class Notificator:
    category = ""
    discard = False

    def delete(self) -> None:
        with connection.cursor() as cursor:
            query = """
                DELETE FROM hipeac_notification WHERE category = %s
            """
            cursor.execute(query, [self.category])

    def insert(self, data: List[Tuple]) -> None:
        with connection.cursor() as cursor:
            query = """
                INSERT INTO hipeac_notification
                (category, user_id, object_id, data, deadline, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """
            cursor.executemany(query, data)

    def to_json(self, data: dict) -> str:
        data["discard"] = self.discard
        return json.dumps(data)

    def from_json(self, data: str) -> dict:
        return json.loads(data)

    def process_data(self):
        raise NotImplementedError

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        raise NotImplementedError


def parse_notification(notification: Notification):
    from .events import RegistrationPendingNotificator
    from .users import (
        LinkedInNotificator,
        LongTimeNoSeeNotificator,
        MembershipIndustryNotificator,
        MembershipResearcherNotificator,
        ResearchTopicsPendingNotificator,
    )

    notification_class = {
        LinkedInNotificator.category: LinkedInNotificator,
        LongTimeNoSeeNotificator.category: LongTimeNoSeeNotificator,
        MembershipIndustryNotificator.category: MembershipIndustryNotificator,
        MembershipResearcherNotificator.category: MembershipResearcherNotificator,
        RegistrationPendingNotificator.category: RegistrationPendingNotificator,
        ResearchTopicsPendingNotificator.category: ResearchTopicsPendingNotificator,
    }[notification.category]

    return notification_class().parse_notification(notification)
