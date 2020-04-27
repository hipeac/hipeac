# flake8: noqa

import os

env = os.environ.get("DJANGO_ENV", "development")

if env == "production":
    from .production import *
elif env == "test":
    from .test import *
else:
    from .development import *
