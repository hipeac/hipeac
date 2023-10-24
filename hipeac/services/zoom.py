import os

from typing import Optional
from zoomus import ZoomClient


class Zoomer:
    def __init__(self) -> None:
        client_id = os.environ.get("ZOOM_CLIENT_ID")
        client_secret = os.environ.get("ZOOM_CLIENT_SECRET")
        account_id = os.environ.get("ZOOM_ACCOUNT_ID")
        self.client = ZoomClient(client_id, client_secret, account_id)

    def post_webinar_registrant(self, webinar_id: int, user_data: dict) -> Optional[str]:
        """
        Adds a registration for a webinar and returns the Zoom `join_url`.
        """

        user_data["id"] = webinar_id
        res = self.client.webinar.register(**user_data)

        if res.ok:
            return res.json()["join_url"]

        return res.json()
