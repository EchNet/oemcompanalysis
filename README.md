# Dr. MVP

Django-ReactJS application shell, ready to deploy on Heroku.  Zero functionality, all infrastructure.

## What problems does this solve?

From zero to usable application stack in minimal time.

Deployment on Heroku so we spend less time on devops and more on application development.

## Features

* React client built with Parcel.
* Django API server.
* Extensible authentication based on Python Social Auth.
* PostgreSQL database backend.
* Redis backend.
* An asynchronous processing framework based on Celery.

## Spawing a new application

1. Start with empty repository.  `git init`.
1. Pull this repository into that one.
1. Install latest Postgres.
1. Create a database called APPNAME and grant full access to the default user.
1. Edit the DATABASE_URL in the dev Django environment file `djconf/dev.env` to match.
1. Create link to dev Django environment file.
```
  $ cd djmain
  $ ln -s ../djconf/dev.env ./.env
```
1. Run the script `bin/newvenv` to create a new virtual environment.
1. Install latest versions of Node and NPM, then run `npm install`.
1. Install latest Redis.

## Dev tools

See the Makefile.

## First Deploy to Heroku

* Create the Heroku app.
* Create the remote.
* Add postgres addon through command line.
* Add redis addon through command line.
* Add initial env var settings (script TBD).
* Add django and node buildpacks.
* Push.

## Add Facebook login.

* In Facebook Developers: Create a Facebook app.
* In Facebook Developers: Set App Domain to full domain name.
* In Heroku: set env var SOCIAL_AUTH_FACEBOOK_KEY to App ID and SOCIAL_AUTH_FACEBOOK_SECRET to App Secret.
* In Facebook Developers: Add product Facebook Login to app.
* In Facebook Developers: Add https://domain.name/complete/facebook/ to Valid OAuth Redirect URIs.

Procedure for adding Google OAuth login is similar.
