"""
*2014.02.25 11:33:22
based on convert-address
need some default values that migrations did not handle
making this in case they are not handled in production too

"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

city_options = City.objects.filter(tag="columbia_mo")
if not len(city_options):
    raise ValueError, "CITY NOT FOUND! run make_cities.py first"
else:
    city = city_options[0]

buildings = Building.objects.filter(city=city)
#buildings = Building.objects.all()
print len(buildings)
print buildings.count()
total = buildings.count()
start = 2822
count = start
#for building in buildings[:10]:
for building in buildings[start:]:
    print 
    print "Starting %05d (out of %05d): %s" % (count, total, building.address)


    ## building.renewable_energy_details = ""
    ## building.garden_details = ""
    ## building.bike_friendly_details = ""
    ## building.walk_friendly_details = ""
    ## building.transit_friendly_details = ""
    
    ## building.save()

    print "Building.tag pre: %s" % building.tag
    building.create_tag(force=True)
    print "Building.tag post: %s" % building.tag

                
    count += 1
        
