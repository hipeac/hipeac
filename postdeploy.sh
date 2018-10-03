#!/bin/bash

cd /app

python manage.py clearcache
python manage.py nltk_download
find $NLTK_DATA -type f -name '*.zip' -delete
