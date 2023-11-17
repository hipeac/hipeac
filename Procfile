web: gunicorn -c gunicorn.config.py hipeac.wsgi
worker: celery worker -A hipeac -n hipeac --loglevel INFO
beat: celery beat -A hipeac
