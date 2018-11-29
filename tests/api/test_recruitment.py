import pytest

from django.urls import reverse
from model_mommy import mommy
from rest_framework import status

from .generic import UserMixin


@pytest.mark.django_db
class TestForAnonymous:
    job_active = None
    job_not_active = None
    list_url = reverse('v1:job-list')

    @pytest.fixture(autouse=True)
    def setup_job(self, db, now):
        if not self.job_active:
            self.job_active = mommy.make_recipe('hipeac.job', deadline=now.add(days=1).datetime)
            self.job_not_active = mommy.make_recipe('hipeac.job', deadline=now.subtract(days=1).datetime)
        return

    def get_detail_url(self, job_id):
        return reverse('v1:job-detail', args=[job_id])

    def test_list(self, api_client):
        assert api_client.get(self.list_url).status_code == status.HTTP_200_OK

    def test_create(self, api_client):
        assert api_client.post(self.list_url).status_code == status.HTTP_403_FORBIDDEN

    def test_read(self, api_client):
        assert api_client.get(self.get_detail_url(self.job_active.id)).status_code == status.HTTP_200_OK
        assert api_client.get(self.get_detail_url(self.job_not_active.id)).status_code == status.HTTP_404_NOT_FOUND

    def test_update(self, api_client):
        detail_url = self.get_detail_url(self.job_active.id)
        assert api_client.patch(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.post(detail_url).status_code == status.HTTP_403_FORBIDDEN
        assert api_client.put(detail_url).status_code == status.HTTP_403_FORBIDDEN

    def test_delete(self, api_client):
        assert api_client.delete(self.get_detail_url(self.job_active.id)).status_code == status.HTTP_403_FORBIDDEN


class TestForAuthenticated(UserMixin, TestForAnonymous):
    job = None
    test_data = {}

    @pytest.fixture(autouse=True)
    def setup_test_data(self, db, now):
        if not self.test_data:
            employment_type = mommy.make_recipe('hipeac.employment_type')
            self.test_data = {
                'title': 'Job title',
                'description': 'Job description.',
                'deadline': str(now.add(months=1).date),
                'employment_type': {'id': employment_type.id},
                'country': 'BE',
                'email': 'recruitment@hipeac.net',
                'institution': 1,
                'application_areas': [],
                'career_levels': [],
                'topics': []
            }
        return

    def test_create(self, api_client):
        api_client.force_authenticate(user=self.user)
        res = api_client.post(self.list_url, self.test_data)
        self.job = res.json()
        assert res.status_code == status.HTTP_201_CREATED


class TestForAdministrator(TestForAuthenticated):

    def test_update(self, api_client):
        api_client.force_authenticate(user=self.user)
        self.job = api_client.post(self.list_url, self.test_data).json()
        detail_url = self.get_detail_url(self.job['id'])
        assert api_client.patch(detail_url, {'title': 'New title'}).status_code == status.HTTP_200_OK
        assert api_client.post(detail_url).status_code == status.HTTP_405_METHOD_NOT_ALLOWED
        assert api_client.put(detail_url, self.test_data).status_code == status.HTTP_200_OK

    def test_delete(self, api_client):
        api_client.force_authenticate(user=self.user)
        self.job = api_client.post(self.list_url, self.test_data).json()
        detail_url = self.get_detail_url(self.job['id'])
        assert api_client.delete(detail_url).status_code == status.HTTP_204_NO_CONTENT
