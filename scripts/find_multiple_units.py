"""
*2014.02.27 14:31:54 
just a helper script...
looking for buildings with multipe units associated

"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

city_options = City.objects.filter(tag="bloomington_in")
#city_options = City.objects.filter(tag="ann_arbor_mi")
print "Number of cities available: %s" % len(city_options)
if not len(city_options):
    raise ValueError, "CITY NOT FOUND! run make_cities.py first"
else:
    city = city_options[0]

buildings = Building.objects.filter(city=city)
#buildings = Building.objects.all()
print len(buildings)
print buildings.count()
count = 0
#for building in buildings[:10]:
for building in buildings:
    if len(building.units.all()) > 1:
        print 
        print "%04d: %s" % (count, building.address)
        print "%s units" % (len(building.units.all()))
                
    count += 1
        
