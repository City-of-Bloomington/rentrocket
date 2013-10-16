from django.db import models
import re

#rather than do a lookup for some of these items
#just reference a local cache...
#not that many.
#
#still need to have in the database for ForeignKey purposes
#
#to update
#cd scripts 
#python make_cities.py
#then copy in from cities.json
all_cities = {"albany_ny": {"lat": 42.6525793, "state": "NY", "tag": "albany_ny", "name": "Albany", "lng": -73.7562317}, "fayetteville_ar": {"lat": 36.0625795, "state": "AR", "tag": "fayetteville_ar", "name": "Fayetteville", "lng": -94.1574263}, "austin_tx": {"lat": 30.267153, "state": "TX", "tag": "austin_tx", "name": "Austin", "lng": -97.7430608}, "madison_wi": {"lat": 43.0730517, "state": "WI", "tag": "madison_wi", "name": "Madison", "lng": -89.4012302}, "oklahoma_city_ok": {"lat": 35.4675602, "state": "OK", "tag": "oklahoma_city_ok", "name": "Oklahoma City", "lng": -97.5164276}, "berkeley_ca": {"lat": 37.8715926, "state": "CA", "tag": "berkeley_ca", "name": "Berkeley", "lng": -122.272747}, "evanston_il": {"lat": 42.0450722, "state": "IL", "tag": "evanston_il", "name": "Evanston", "lng": -87.68769689999999}, "lawrence_ks": {"lat": 38.9716689, "state": "KS", "tag": "lawrence_ks", "name": "Lawrence", "lng": -95.2352501}, "columbia_mo": {"lat": 38.9517053, "state": "MO", "tag": "columbia_mo", "name": "Columbia", "lng": -92.3340724}, "burlington_vt": {"lat": 44.4758825, "state": "VT", "tag": "burlington_vt", "name": "Burlington", "lng": -73.21207199999999}, "bloomington_in": {"lat": 39.165325, "state": "IN", "tag": "bloomington_in", "name": "Bloomington", "lng": -86.52638569999999}, "dearborn_mi": {"lat": 42.3222599, "state": "MI", "tag": "dearborn_mi", "name": "Dearborn", "lng": -83.17631449999999}, "ann_arbor_mi": {"lat": 42.2808256, "state": "MI", "tag": "ann_arbor_mi", "name": "Ann Arbor", "lng": -83.7430378}, "iowa_city_ia": {"lat": 41.6611277, "state": "IA", "tag": "iowa_city_ia", "name": "Iowa City", "lng": -91.5301683}}


#feed info moved to source.models.FeedInfo

def to_tag(item):
    """
    take any string and convert it to an acceptable tag

    tags should not contain spaces or special characters
    numbers, lowercase letters only
    underscores can be used, but they will be converted to spaces in some cases
    """
    #item = self.name.lower()
    item = item.lower()
    #get rid of trailing and leading blank spaces:
    item = item.strip()
    item = re.sub(' ', '_', item)
    item = re.sub("/", '_', item)
    item = re.sub("\\\\'", '', item)
    item = re.sub("\\'", '', item)
    item = re.sub("'", '', item)

    #todo:
    # filter any non alphanumeric characters

    return item


class City(models.Model):
    """
    Details to define a specific City
    """
    #Name of the municipality providing this feed.
    #For example 'San Francisco' or 'Multnomah County'
    #municipality_name = models.CharField(max_length=20)

    name = models.CharField(max_length=200)

    #URL of the publishing municipality's website
    url = models.CharField(max_length=100, blank=True)

    #this is what we'll use to look up a city:
    tag = models.CharField(max_length=200, unique=True, default=to_tag(str(name)))

    #in case we want to represent other types of municipalities, not just cities
    type = models.CharField(max_length=50, default="city")

    #State where the property is located.
    #In the U.S. this should be the two-letter code for the state
    state = models.CharField(max_length=2)

    #where to center the map when choosing this location
    latitude = models.FloatField()
    longitude = models.FloatField()

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

