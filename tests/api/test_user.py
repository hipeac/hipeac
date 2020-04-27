import pytest

from django.urls import reverse
from model_bakery import baker
from rest_framework import status


@pytest.mark.django_db
class TestForAnonymous:
    account_url = reverse("v1:auth-user-account")

    @pytest.mark.skip(reason="HTTP_405_METHOD_NOT_ALLOWED")
    def test_list(self, api_client):
        pass

    @pytest.mark.skip(reason="HTTP_405_METHOD_NOT_ALLOWED")
    def test_create(self, api_client):
        pass

    def test_account_read(self, api_client):
        assert api_client.get(self.account_url).status_code == status.HTTP_403_FORBIDDEN

    def test_account_update(self, api_client):
        assert api_client.patch(self.account_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.post(self.account_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(self.account_url).status_code == status.HTTP_403_FORBIDDEN

    def test_acoount_delete(self, api_client):
        assert api_client.delete(self.account_url).status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestForAuthenticated(TestForAnonymous):
    @pytest.fixture(autouse=True)
    def setup_data(self):
        self.user = baker.make_recipe("hipeac.user")

    def test_account_read(self, api_client):
        api_client.force_authenticate(user=self.user)
        res = api_client.get(self.account_url)
        assert res.status_code == status.HTTP_200_OK
        assert res.json()["id"] == self.user.id

    def test_account_update(self, api_client):
        api_client.force_authenticate(user=self.user)
        full_data = {
            "username": "hipeac",
            "first_name": "HiPEAC",
            "last_name": "6",
            "profile": {
                "country": "BE",
                "application_areas": [],
                "topics": [],
                "projects": [],
                "links": [],
                "meal_preference": None,
            },
        }
        assert api_client.patch(self.account_url, {"username": "hipeac"}).status_code == status.HTTP_200_OK
        assert api_client.post(self.account_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(self.account_url, full_data).status_code == status.HTTP_200_OK

    def test_delete(self, api_client):
        api_client.force_authenticate(user=self.user)
        assert api_client.delete(self.account_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
