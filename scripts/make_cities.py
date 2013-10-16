import sys, os

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
from rentrocket import settings
from django.core.management import setup_environ
setup_environ(settings)

from city.models import City, to_tag

from helpers import save_json, load_json, Location, Geo, save_results, make_building


cache_file = "cities.json" 
cache_destination = os.path.join(os.path.dirname(__file__), cache_file)
#keep a local copy of data we've processed...
#this should help with subsequent calls
#to make sure we don't need to duplicate calls to remote geolocation APIs:
saved_cities = load_json(cache_destination, create=True)


#geocoder helper:
geo = Geo()

cities = [ ['Bloomington', 'IN', '', ''],
           ['Ann Arbor', 'MI', '', ''],
           ['Albany', 'NY', '', ''],
           ['Iowa City', 'IA', '', ''],
           ['Burlington', 'VT', '', ''],
           ['Austin', 'TX', '', ''],
           ['Columbia', 'MO', '', ''],
           ['Madison', 'WI', '', ''],
           ['Lawrence', 'KS', '', ''],
           ['Berkeley', 'CA', '', ''],
           ['Evanston', 'IL', '', ''],
           ['Fayetteville', 'AR', '', ''],
           ['Dearborn', 'MI', '', ''],
           ['Oklahoma City', 'OK', '', ''],
           ]

for city_simple in cities:
    city_name = city_simple[0]
    city_state = city_simple[1]
    city_tag = to_tag("%s_%s" % (city_name, city_state))

    city_options = City.objects.filter(tag=city_tag)
    print "Number of cities available: %s" % len(city_options)
    if not len(city_options):
        city = City()
    else:
        city = city_options[0]
        
    city.name = city_name
    city.tag = city_tag
    city.state = city_state

    if saved_cities.has_key(city_tag) and saved_cities[city_tag]['lat'] and saved_cities[city_tag]['lng']:
        city_dict = saved_cities[city_tag]
        print city_dict
        
        city.latitude = city_dict['lat']
        city.longitude = city_dict['lng']
    else:
        
        location = Location()

        #temporarily just want to look at google again
        location.sources = ["google"]

        #do some geocoding, as needed:
        search = "%s %s" % (city_name, city_state)

        any_updated = False
        for geo_source in location.sources:
            update = geo.lookup(search, geo_source, location, force=True)
            if update:
                any_updated = True

            result = location.get_source(geo_source)
            print len(result)
            print result
            city.latitude = result[0]['lat']
            city.longitude = result[0]['lng']

        location.sources = ["google", "bing", "usgeo", "geonames", "openmq", "mq"]
        
        saved_cities[city_tag] = {"name":city.name, "state":city.state, "tag":city.tag, "lat":city.latitude, "lng":city.longitude}

        save_json(cache_destination, saved_cities)
    
    city.save()

