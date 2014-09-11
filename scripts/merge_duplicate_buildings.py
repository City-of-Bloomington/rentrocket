"""
*2014.09.09 16:07:57 
just a helper script...
looking for buildings with the same building tag 

SETTINGS_MODE='prod' python find_duplicate_buildings.py

see also:
update_building_addresses.py
update_building_details.py
update_unit_details.py
"""
import os, sys, re
import json

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

from helpers import save_json

city_options = City.objects.filter(tag="bloomington_in")
#city_options = City.objects.filter(tag="ann_arbor_mi")
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
previous = {}
for building in buildings:
    if not building.tag in previous:
        previous[building.tag] = [ building.id ]
    else:
        print "%s previous buildings found with tag: %s" % (len(previous[building.tag]), building.tag)
        first_building = Building.objects.get(id=previous[building.tag][0])
        #print "%s units associated" % (dir(building.units))
        print "%s units associated" % (len(building.units.all()))
        for unit in building.units.all():
            print unit.tag
            unit.building = first_building
            unit.save()

        previous[building.tag].append(building.id)
        #TODO
        #delete this building now
        building.delete()

        
    count += 1


## keys = range(1496, 1512)
## for key in keys:
##     b = Building.objects.get(id=key)
##     print b

#print json.dumps(previous)
save_json("building_dupes.json", previous)
print "saving to: building_dupes.json"
