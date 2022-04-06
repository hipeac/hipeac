web: gunicorn -b :5000 --workers=3 --worker-class=gevent hipeac.wsgi
worker: celery worker -A hipeac -n hipeac --loglevel INFO
beat: celery beat -A hipeac
