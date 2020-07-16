web: daphne djmain.asgi:application --port $PORT --bind 0.0.0.0 -v2
celery: celery --app=djmain worker --beat --loglevel=debug
release: python manage.py migrate --no-input
