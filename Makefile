# Make commands for development
# 
# `make djsetup` install required Python modules.
# `make djbuild` generates required migrations.
# `make djtest` runs automated Python tests.
#
# `make djrun` runs the Django server, listening on port 8000.
# `make celery` runs a Celery worker.  Needs to be restarted manually when code changes.
# `make rrun` runs the React webpack server, listening on port 3000.

PIP=pip
PYTHON=python
NPM=npm
CELERY=celery

.DEFAULT_GOAL: test

test: djtest rtest

requirements.txt: requirements.in
	$(PIP) install -r requirements.in
	echo "# GENERATED FROM requirements.in.  DO NOT EDIT DIRECTLY." > requirements.txt
	$(PIP) freeze >> requirements.txt

requirements.flag: requirements.txt
	$(PIP) install -r requirements.txt
	touch requirements.flag

djbuild: requirements.flag
	$(PYTHON) ./manage.py makemigrations

djtest: djbuild
	$(PYTHON) ./manage.py test ./djmain/tests

djrun: djbuild
	$(PYTHON) ./manage.py migrate
	$(PYTHON) ./manage.py runserver

celery: djbuild
	$(CELERY) -A djmain worker --loglevel=debug

package-lock.json: package.json
	$(NPM) install

rrun: package-lock.json
	./node_modules/.bin/parcel rapp/index.html

rtest: package-lock.json
	@echo React tests not yet implemented.

rdist: package-lock.json
	./node_modules/.bin/parcel build rapp/index.js

clean:
	rm -rf dist .cache build
