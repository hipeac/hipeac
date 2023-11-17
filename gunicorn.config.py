import multiprocessing
import os


bind = ":5000"
workers = (multiprocessing.cpu_count() * 2 + 1) if os.environ.get("DJANGO_ENV") == "production" else 1
worker_class = "gevent"
worker_connections = 1000
