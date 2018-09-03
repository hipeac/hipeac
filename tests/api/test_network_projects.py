import pytest

from django.urls import reverse
from model_mommy import mommy
from rest_framework import status

from hipeac.models import Permission
from .generic import UserMixin


@pytest.mark.django_db
class TestForAnonymous:
    list_url = reverse('v1:project-list')
    project = None

    @pytest.fixture(autouse=True)
    def setup_project(self, db):
        if not self.project:
            self.project = mommy.make_recipe('hipeac.project')
        return

    def get_detail_url(self, id):
        return reverse('v1:project-detail', args=[id])

    def test_list(self, api_client):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url, {}).status_code == status.HTTP_403_FORBIDDEN

    def test_read(self, api_client):
        assert api_client.get(self.get_detail_url(self.project.id)).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        detail_url = self.get_detail_url(self.project.id)
        assert api_client.patch(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.post(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(detail_url).status_code == status.HTTP_403_FORBIDDEN

    def test_delete(self, api_client):
        assert api_client.delete(self.get_detail_url(self.project.id)).status_code == status.HTTP_403_FORBIDDEN


class TestForAuthenticated(UserMixin, TestForAnonymous):
    user = None

    @pytest.fixture(autouse=True)
    def setup_user(self, db):
        if not self.user:
            self.user = mommy.make_recipe('hipeac.user')
        return

    def test_create(self, api_client):
        api_client.force_authenticate(user=self.user)
        assert api_client.post(self.list_url, {}).status_code == status.HTTP_405_METHOD_NOT_ALLOWED

    def test_delete(self, api_client):
        api_client.force_authenticate(user=self.user)
        assert api_client.delete(self.get_detail_url(self.project.id)).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestForAdministrator(TestForAuthenticated):
    project = None
    user_admin = None

    @pytest.fixture(autouse=True)
    def setup_project(self, db):
        if not self.project:
            self.user_admin = mommy.make_recipe('hipeac.user')
            self.project = mommy.make_recipe('hipeac.project')
            Permission.objects.create(content_type=self.project.get_content_type(), object_id=self.project.id,
                                      user=self.user_admin, level=Permission.ADMIN)
        return

    def test_update(self, api_client, db):
        api_client.force_authenticate(user=self.user_admin)
        detail_url = self.get_detail_url(self.project.id)
        assert api_client.patch(detail_url, {'name': 'name'}).status_code == status.HTTP_200_OK
        assert api_client.post(detail_url, {}).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        # assert api_client.put(self.list_url, {'name': 'name'}).status_code == status.HTTP_202_ACCEPTED
