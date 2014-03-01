"""
*2014.02.28 10:45:09 
looking for buildings with multipe units associated

then generate their average utilities

"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

#buildings = Building.objects.filter(city=city)
buildings = Building.objects.all()
print len(buildings)
print buildings.count()
count = 0
#for building in buildings[:10]:
for building in buildings:
    if len(building.units.all()) > 1:
        print 
        print "%04d: %s" % (count, building.address)
        print "%s units" % (len(building.units.all()))
        building.update_averages()
        exit()
                
    count += 1
        
