web: gunicorn -b :5000 hipeac.wsgi:application
worker: celery worker -A hipeac -n hipeac --loglevel INFO
beat: celery beat -A hipeac
