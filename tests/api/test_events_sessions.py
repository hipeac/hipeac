import pytest

from django.urls import reverse
from model_mommy import mommy
from rest_framework import status

from hipeac.models import Permission
from .generic import UserMixin


class TestForAnonymous:
    session = None

    @pytest.fixture(autouse=True)
    def setup_session(self, db):
        if not self.session:
            self.session = mommy.make_recipe('hipeac.session')
        return

    def get_detail_url(self, id: int):
        return reverse('v1:session-detail', args=[id])

    @pytest.mark.skip(reason='HTTP_405_METHOD_NOT_ALLOWED')
    def test_list(self, api_client):
        pass

    @pytest.mark.skip(reason='HTTP_405_METHOD_NOT_ALLOWED')
    def test_create(self, api_client):
        pass

    def test_read(self, api_client, db):
        assert api_client.get(self.get_detail_url(self.session.id)).status_code == status.HTTP_200_OK

    def test_update(self, api_client):
        detail_url = self.get_detail_url(self.session.id)
        assert api_client.patch(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.post(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(detail_url).status_code == status.HTTP_403_FORBIDDEN

    def test_delete(self, api_client):
        detail_url = self.get_detail_url(self.session.id)
        assert api_client.delete(detail_url).status_code == status.HTTP_403_FORBIDDEN


class TestForAuthenticated(UserMixin, TestForAnonymous):

    def test_delete(self, api_client):
        api_client.force_authenticate(user=self.user)
        assert api_client.delete(self.get_detail_url(self.session.id)).status_code == status.HTTP_405_METHOD_NOT_ALLOWED


class TestForAdministrator(TestForAuthenticated):
    test_data = None

    @pytest.fixture(autouse=True)
    def setup_session(self, db):
        if not self.session:
            self.user_admin = mommy.make_recipe('hipeac.user')
            self.session = mommy.make_recipe('hipeac.session')
            Permission(content_object=self.session, user=self.user_admin, level=Permission.ADMIN).save()
        return

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db, now):
        if not self.test_data:
            self.test_data = {
                'title': 'Session title',
                'application_areas': [],
                'topics': [],
                'projects': [],
            }
        return

    def test_update(self, api_client):
        api_client.force_authenticate(user=self.user_admin)
        detail_url = self.get_detail_url(self.session.id)
        assert api_client.patch(detail_url, {'title': 'New title'}).status_code == status.HTTP_200_OK
        assert api_client.post(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(detail_url, self.test_data).status_code == status.HTTP_200_OK
