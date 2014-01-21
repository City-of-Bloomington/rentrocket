green-rental
============

For starting a local development server:

python manage.py runserver 8080


Requirements:
-----------------

(copied these to local project directory, so they should be available)
sudo pip install geopy

#for database migrations
sudo pip install South



Database synchronization:
----------------------------------

python manage.py syncdb

#https://docs.djangoproject.com/en/dev/howto/initial-data/#where-django-finds-f
#may need to do this manually... good way to verify it works if values not show
python manage.py loaddata rentrocket/fixtures/initial_data.json

python manage.py sql place

field type reference:
https://docs.djangoproject.com/en/1.5/ref/models/fields/#django.db.models.CharField


rm -rf building/migrations
rm -rf city/migrations
rm -rf content/migrations
rm -rf inspection/migrations
rm -rf manager/migrations
rm -rf person/migrations
rm -rf service/migrations
rm -rf source/migrations

./manage.py schemamigration building --initial
./manage.py schemamigration city --initial
./manage.py schemamigration content --initial
./manage.py schemamigration inspection --initial
./manage.py schemamigration manager --initial
./manage.py schemamigration person --initial
./manage.py schemamigration service --initial
./manage.py schemamigration source --initial

./manage.py schemamigration building --auto
./manage.py schemamigration city --auto
./manage.py schemamigration content --auto
./manage.py schemamigration inspection --auto
./manage.py schemamigration manager --auto
./manage.py schemamigration person --auto
./manage.py schemamigration service --auto
./manage.py schemamigration source --auto


./manage.py migrate building
./manage.py migrate city
./manage.py migrate content
./manage.py migrate inspection
./manage.py migrate manager
./manage.py migrate person
./manage.py migrate service
./manage.py migrate source


./manage.py migrate allauth.socialaccount

python ./scripts/make_cities.py

#if enabled: (not currently)
./manage.py migrate allauth.socialaccount.providers.facebook
./manage.py migrate allauth.socialaccount.providers.twitter

Database initialization:
----------------------------------

can remove all tables with a tool like Sequel Pro

then 
python manage.py syncdb


Production:
-------------------

SETTINGS_MODE='prod' ./manage.py migrate building
SETTINGS_MODE='prod' ./manage.py migrate city
SETTINGS_MODE='prod' ./manage.py migrate content
SETTINGS_MODE='prod' ./manage.py migrate inspection
SETTINGS_MODE='prod' ./manage.py migrate manager
SETTINGS_MODE='prod' ./manage.py migrate person
SETTINGS_MODE='prod' ./manage.py migrate service
SETTINGS_MODE='prod' ./manage.py migrate source
SETTINGS_MODE='prod' ./manage.py migrate allauth.socialaccount


SETTINGS_MODE='prod' ./manage.py migrate allauth.socialaccount.providers.facebook
SETTINGS_MODE='prod' ./manage.py migrate allauth.socialaccount.providers.twitter


SETTINGS_MODE='prod' 