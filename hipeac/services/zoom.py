import os

from typing import Optional
from zoomus import ZoomClient


class Zoomer:
    def __init__(self) -> None:
        api_key = os.environ.get("ZOOM_API_KEY")
        api_secret = os.environ.get("ZOOM_API_SECRET")
        self.client = ZoomClient(api_key, api_secret)  # noqa

    def post_webinar_registrant(self, webinar_id: int, user_data: dict) -> Optional[str]:
        """
        Adds a registration for a webinar and returns the Zoom `join_url`.
        """

        user_data["id"] = webinar_id
        res = self.client.webinar.register(**user_data)

        if res.ok:
            return res.json()["join_url"]

        return None
