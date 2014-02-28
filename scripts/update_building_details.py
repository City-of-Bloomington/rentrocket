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

#buildings = Building.objects.filter(city=city)
buildings = Building.objects.all()
print len(buildings)
print buildings.count()
count = 0
#for building in buildings[:10]:
for building in buildings:
    print 
    print "Starting %04d: %s" % (count, building.address)

    building.renewable_energy_details = ""
    building.garden_details = ""
    building.bike_friendly_details = ""
    building.walk_friendly_details = ""
    building.transit_friendly_details = ""
    
    building.save()
                
    count += 1
        
