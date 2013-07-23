green-rental
============

For starting a local development server:

python manage.py runserver 8080


Requirements:
-----------------

sudo pip install geopy

#for database migrations
sudo pip install South



Database synchronization:
----------------------------------

python manage.py syncdb

python manage.py sql place

field type reference:
https://docs.djangoproject.com/en/1.5/ref/models/fields/#django.db.models.CharField


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
