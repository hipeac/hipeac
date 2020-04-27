import pytest

from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestForAnonymous:
    list_url = reverse("v1:session-list")
    detail_url = reverse("v1:session-detail", args=[1])

    def test_list(self, api_client):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url, {"name": "name"}).status_code == status.HTTP_403_FORBIDDEN

    def test_read(self, api_client):
        assert api_client.get(self.detail_url).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        assert api_client.patch(self.detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.post(self.detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(self.detail_url).status_code == status.HTTP_403_FORBIDDEN

    def test_delete(self, api_client):
        assert api_client.delete(self.detail_url).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.skip(reason="No extra permissions for authenticated users")
class TestForAuthenticated(TestForAnonymous):
    pass


class TestForAdministrator(TestForAuthenticated):
    def test_update(self, api_client, db):
        assert api_client.patch(self.list_url, {"name": "name"}).status_code == status.HTTP_202_ACCEPTED
        assert api_client.post(self.list_url, {"name": "name"}).status_code == status.HTTP_202_ACCEPTED
        assert api_client.put(self.list_url, {"name": "name"}).status_code == status.HTTP_202_ACCEPTED
