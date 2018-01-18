#!/bin/bash

cd /app

python manage.py nltk_download
find $NLTK_DATA -type f -name '*.zip' -delete

python manage.py collectstatic --noinput -v 0
python manage.py compress -v 0
python manage.py migrate
python manage.py clearsessions
