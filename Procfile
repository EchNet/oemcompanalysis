web: gunicorn djmain.wsgi --max-requests 1200
celery: celery --app=djmain worker --beat --loglevel=debug
release: python manage.py migrate --no-input
