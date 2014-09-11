"""
*2014.09.09 17:38:16
helper script to test the different searches available with existing data first

SETTINGS_MODE='prod' python test_searches.py
"""
import os, sys, re
import json

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit, search_building
from city.models import City
from rentrocket.helpers import to_tag

from helpers import save_json

#https://code.google.com/p/gmaps-api-issues/issues/detail?id=5587
result = search_building("3210 E JOHN HINKLE PL UNIT B, Bloomington IN")
print result

result = search_building("500 North Walnut Street apartment 204, Bloomington, IN")
print result

result = search_building("619 e")
print result

#save_json("building_dupes.json", previous)
#print "saving to: building_dupes.json"
