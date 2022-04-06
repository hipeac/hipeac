from celery import task
from typing import Tuple

from hipeac.models import Event, SessionAccessLink
from hipeac.services.zoom import Zoomer


@task(rate_limit="10/s")
def add_webinar_registrant(data: Tuple[int, int, int, dict]):
    """Adds a zoom registration for an event."""
    session_id, user_id, webinar_id, user_data = data
    join_url = Zoomer().post_webinar_registrant(webinar_id, user_data)

    if join_url:
        SessionAccessLink.objects.update_or_create(session_id=session_id, user_id=user_id, defaults={"url": join_url})

    return session_id, user_id, join_url


@task()
def sync_webinar_registrants(event_id: int):
    event = Event.objects.get(id=event_id)
    existing_links = set((sal.session_id, sal.user_id) for sal in SessionAccessLink.objects.all())

    for session in event.sessions.all():
        if session.zoom_webinar_id:
            for registration in session.registrations.select_related("user__profile"):
                if (session.id, registration.user_id) not in existing_links:
                    add_webinar_registrant(
                        (
                            session.id,
                            registration.user_id,
                            session.zoom_webinar_int,
                            {
                                "email": registration.user.email,
                                "first_name": registration.user.first_name,
                                "last_name": registration.user.last_name,
                                "country": registration.user.profile.country.code,
                            },
                        )
                    )

    return
