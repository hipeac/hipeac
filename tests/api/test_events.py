import pytest

from django.urls import reverse
from model_bakery import baker
from rest_framework import status


class TestForAnonymous:
    event = None
    list_url = reverse("v1:event-list")
    detail_url = reverse("v1:event-detail", args=[1])

    @pytest.fixture(autouse=True)
    def setup_event(self, db, now):
        if not self.event:
            self.event = baker.make_recipe("hipeac.event")
        return

    def test_list(self, api_client, db):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url, {"name": "name"}).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_read(self, api_client, db):
        assert api_client.get(self.detail_url).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        assert api_client.patch(self.detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(self.detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete(self, api_client):
        assert api_client.delete(self.detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
