from django.db import connection
from typing import Any, Dict

from hipeac.models import Notification, Event
from .generic import Notificator


class RegistrationPendingNotificator(Notificator):
    category = "registration_pending"
    discard = True

    def deleteOne(self, *, user_id: int, event_id: int) -> None:
        Notification.objects.filter(category=self.category, user_id=user_id, object_id=event_id).delete()

    def process_data(self):
        self.delete()
        bulk_notifications = []

        with connection.cursor() as cursor:
            for event in Event.objects.registering():
                query = """
                    SELECT u.id AS user_id
                    FROM auth_user AS u
                    WHERE u.last_login > (CURRENT_DATE - INTERVAL '6 MONTH')
                    AND u.id NOT IN (
                        SELECT user_id
                        FROM hipeac_event_registration
                        WHERE event_id = %s
                    )
                """
                cursor.execute(query, [event.id])

                for result in cursor.fetchall():
                    bulk_notifications.append(
                        (
                            self.category,  # category
                            result[0],  # user_id
                            event.id,  # object_id == event_id
                            self.to_json({"discard_id": event.id, "event_id": event.id}),  # data
                            event.registration_deadline,  # deadline
                        )
                    )

        self.insert(bulk_notifications)

    def parse_notification(self, notification: Notification) -> Dict[str, Any]:
        event = Event.objects.get(id=notification.data["event_id"])
        return {
            "text": f"Don't forget to register for {event}!",
            "path": event.get_absolute_url(),
        }
