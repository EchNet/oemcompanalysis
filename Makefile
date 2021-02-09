# Make commands for development
# 
# `make build` installs required modules and generates required migrations.
# `make test` runs automated Python tests.
# `make run` runs the Django server, listening on port 8000.
# `make celery` runs a Celery worker.  Needs to be restarted manually when code changes.

PIP=pip
PYTHON=python
CELERY=celery

.DEFAULT_GOAL: test

requirements.txt: requirements.in
	$(PIP) install -r requirements.in
	echo "# GENERATED FROM requirements.in.  DO NOT EDIT DIRECTLY." > requirements.txt
	$(PIP) freeze >> requirements.txt

requirements.flag: requirements.txt
	$(PIP) install -r requirements.txt
	touch requirements.flag

build: requirements.flag
	$(PYTHON) ./manage.py makemigrations

test: build
	$(PYTHON) ./manage.py test ./djmain/tests

run: build
	$(PYTHON) ./manage.py migrate
	$(PYTHON) ./manage.py runserver

celery: build
	$(CELERY) -A djmain worker --loglevel=debug

clean:
	rm -rf dist .cache build
