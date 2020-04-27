import pytest

from django.urls import reverse
from model_bakery import baker
from rest_framework import status

from hipeac.models import Permission, Institution
from .generic import UserMixin


@pytest.mark.django_db
class TestForAnonymous:
    list_url = reverse("v1:institution-list")
    institution = None

    @pytest.fixture(autouse=True)
    def setup_institution(self, db):
        if not self.institution:
            self.institution = baker.make_recipe("hipeac.institution")
        return

    def get_detail_url(self, id):
        return reverse("v1:institution-detail", args=[id])

    def test_list(self, api_client):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url).status_code == status.HTTP_403_FORBIDDEN

    def test_read(self, api_client):
        assert api_client.get(self.get_detail_url(self.institution.id)).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        detail_url = self.get_detail_url(self.institution.id)
        assert api_client.patch(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(detail_url).status_code == status.HTTP_403_FORBIDDEN

    def test_delete(self, api_client):
        detail_url = self.get_detail_url(self.institution.id)
        assert api_client.delete(detail_url).status_code == status.HTTP_403_FORBIDDEN


class TestForAuthenticated(UserMixin, TestForAnonymous):
    def test_create(self, api_client):
        api_client.force_authenticate(user=self.user)
        assert api_client.post(self.list_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete(self, api_client):
        api_client.force_authenticate(user=self.user)
        detail_url = self.get_detail_url(self.institution.id)
        assert api_client.delete(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestForAdministrator(TestForAuthenticated):
    institution = None
    test_data = {}
    user_admin = None

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db):
        if not self.test_data:
            self.test_data = {
                "name": "Institution",
                "type": Institution.UNIVERSITY,
                "country": "BE",
                "application_areas": [],
                "topics": [],
                "links": [],
            }
        return

    @pytest.fixture(autouse=True)
    def setup_institution(self, db):
        if not self.institution:
            self.user_admin = baker.make_recipe("hipeac.user")
            self.institution = baker.make_recipe("hipeac.institution")
            Permission(content_object=self.institution, user=self.user_admin, level=Permission.ADMIN).save()
        return

    def test_update(self, api_client):
        api_client.force_authenticate(user=self.user_admin)
        detail_url = self.get_detail_url(self.institution.id)
        assert api_client.patch(detail_url, {"name": "name"}).status_code == status.HTTP_200_OK
        assert api_client.post(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(detail_url, self.test_data).status_code == status.HTTP_200_OK
