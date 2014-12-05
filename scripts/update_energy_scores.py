"""
*2014.12.04 07:13:22
go through every city
and go through every building in that city
update each unit's energy score (unit.update_energy_score())
and then update the building's averages (building.update_utility_averages())

"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

#city_options = City.objects.filter(tag="bloomington_in")
#city_options = City.objects.filter(tag="ann_arbor_mi")
#city_options = City.objects.filter(tag="columbia_mo")
city_options = City.objects.all()
print "Number of cities available: %s" % len(city_options)
if not len(city_options):
    raise ValueError, "CITY NOT FOUND! run make_cities.py first"

city_count = 7
for city in city_options[city_count:]:
    
    print "Looking at city: %s, %s, %s, %s" % (city_count, city.name, city.state, city.tag)
    city_count += 1
    buildings = Building.objects.filter(city=city)
    #print len(buildings)
    print buildings.count()
    print 
    count = 0
    #count = 8160
    
    ## #for building in buildings[3095:]:
    ## #for building in buildings:
    for building in buildings[count:]:

        print 
        print "starting: %04d: %s" % (count, building.address)
        print "%s units" % (len(building.units.all()))

        for unit in building.units.all():
            unit.update_energy_score()

        print "now updating building averages"
        building.update_utility_averages()
        
        count += 1
        
