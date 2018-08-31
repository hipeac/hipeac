import pytest

from django.urls import reverse
from mixer.backend.django import mixer
from rest_framework import status
from typing import Dict


@pytest.mark.django_db
class TestRecruitmentApi:

    @staticmethod
    def get_login_credentials(id: int) -> Dict[str, str]:
        return {
            'username': f'user{id}',
            'password': f'pass{id}'
        }

    @pytest.fixture
    def user1(self):
        return mixer.blend('auth.User', **self.get_login_credentials(1))

    def test_anonymous_can_view_jobs_information(self, api_client):
        res = api_client.get(reverse('v1:job-list'))
        assert res.status_code == status.HTTP_200_OK
        res = api_client.get(reverse('v1:job-detail', args=[1]))
        assert res.status_code == status.HTTP_404_NOT_FOUND
