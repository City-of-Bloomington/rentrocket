"""
some old city objects that are not in use and do not follow the right patterns

would like to clean those up, safely..

this didn't do it though...

was better to go through and manually remove...
this required updating source_feeinfo rows that referenced the old city IDs
plus there was one bad address from an old Ann arbor import that needed to be removed manually (including the building_buildingpersons related to building ID 6716)
"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

old_tags = [ 'madison', 'lawrence', 'berkeley', 'evanston', 'fayetteville', 'dearborn', 'oklahoma_city', 'bloomington', 'ann_arbor', 'albany', 'iowa_city', 'burlington', 'austin', 'columbia']

for tag in old_tags:
    city_options = City.objects.filter(tag=tag)
    print city_options
    if city_options.count():
        print city_options[0].tag
        city = city_options[0]
        city.delete()

    
#city_options = City.objects.filter(tag="ann_arbor_mi")
#city_options = City.objects.filter(tag="columbia_mo")
#city_options = City.objects.all()
