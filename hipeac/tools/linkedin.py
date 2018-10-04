import json
import os
import requests

from django.conf import settings
from typing import Optional


class LinkedInTokenExpiredException(Exception):
    """LinkedIn tokens may have expired."""


class LinkedInManager:
    COMPANY_ID = 9479670
    ACCESS_TOKEN = os.environ.get('LINKEDIN_ACCESS_TOKEN')

    def share_page(self, title: str, comment: str, url: Optional[str] = None, image_url: Optional[str] = None):
        # https://developer.linkedin.com/docs/company-pages#company_share
        try:
            # TODO: somehow connect with `django-allauth`
            # With LinkedIn, we only try, because we use a personal access token that may expire...
            headers = {
                'Authorization': f'Bearer {self.ACCESS_TOKEN}',
                'Content-Type': 'application/json',
                'x-li-format': 'json',
            }
            payload = {
                'visibility': {
                    'code': 'anyone',
                },
                'comment': comment,
                'content': {
                    'title': title,
                    'submitted-url': url,
                    'submitted-image-url': image_url,
                }
            }

            if settings.DEBUG:
                print(payload)
                return

            endpoint = f'https://api.linkedin.com/v1/companies/{self.COMPANY_ID}/shares?format=json'
            res = requests.post(endpoint, headers=headers, data=json.dumps(payload))

            if res.status_code is not 201:
                raise LinkedInTokenExpiredException()

        except Exception as e:
            raise LinkedInTokenExpiredException()
