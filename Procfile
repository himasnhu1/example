web: gunicorn srms.wsgi
worker: celery -A srms worker -B --loglevel=info
beat: celery -A srms beat 