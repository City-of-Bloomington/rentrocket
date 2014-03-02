"""
*2014.02.27 16:25:48 
update unit tags
"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

units = Unit.objects.all()
print len(units)
print units.count()
count = 0
#for unit in units[:10]:
for unit in units:
#for unit in units[15320:]:
    #I think this should happen first, since tag may use it if it exists
    auto_addy = unit.building.address + ", " + unit.number
    if unit.address == auto_addy:
        print 
        print "Clearing %04d: %s, %s" % (count, unit.address, unit.number)
        #clear it out
        unit.address = ''
        unit.save()
                
    if unit.number:
        print 
        print "Starting %04d: %s, %s" % (count, unit.number, unit.building.address)

        if unit.tag != to_tag(unit.number):
            print "%s != %s" % (unit.tag, unit.number)

            #unit.tag = to_tag(unit.number)
            unit.create_tag(force=True)

            unit.save()

    count += 1
        
