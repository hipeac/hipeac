import os
import re

from django.conf import settings
from twitter import *  # noqa
from typing import Optional


CHARACTER_LIMIT = 140
SHORT_URL_LENGTH = 24


class Tweeter:

    def __init__(self, *, account: str = 'hipeac') -> None:
        consumer_key, consumer_secret, access_token, access_token_secret = {
            'hipeacjobs': (
                os.environ.get('TWITTER_JOBS_CONSUMER_KEY'),
                os.environ.get('TWITTER_JOBS_CONSUMER_SECRET'),
                os.environ.get('TWITTER_JOBS_ACCESS_TOKEN'),
                os.environ.get('TWITTER_JOBS_ACCESS_TOKEN_SECRET'),
            ),
        }[account]
        auth = OAuth(access_token, access_token_secret, consumer_key, consumer_secret)  # noqa
        self.api = Twitter(auth=auth)  # noqa

    @staticmethod
    def clean_status(text: str, url: Optional[str] = None) -> str:
        limit = (CHARACTER_LIMIT - (min(SHORT_URL_LENGTH, len(url)) + 1)) if url else CHARACTER_LIMIT
        text = ''.join(text.splitlines())  # remove lines
        text = re.sub(' +', ' ', text).strip()  # remove extra spaces
        text = (text[:limit - 3] + '...') if len(text) > limit else text
        return f'{text} {url}' if url else text

    def update_status(self, text: str, url: Optional[str] = None):
        cleaned_status = self.clean_status(text, url)

        if settings.DEBUG:
            print(cleaned_status)
            return

        self.api.statuses.update(status=cleaned_status)
