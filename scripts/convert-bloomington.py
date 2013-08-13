#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2013.06.19 10:39:08 
# License: GPLv3

# Requires:
#
# geopy

# Description:

Accepts CSV export from Rental Housing Database
Normalizes addresses (and check for previously normalized addresses)

Update any existing entries with changes
Add any new entries
Mark any obsolete entries as non-rentals (or remove any old entries?)

"""

import os, sys, codecs
import csv

from helpers import save_json, load_json, Location, Geo, save_results

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
from rentrocket import settings
from django.core.management import setup_environ
setup_environ(settings)

from building.models import Building, Parcel
from city.models import City, to_tag

def usage():
    print __doc__
    

def read_csv(source):
    city_options = City.objects.filter(tag="bloomington")
    print len(city_options)
    if not len(city_options):
        city = City()
        city.name = "Bloomington"
        city.tag = to_tag(city.name)
        city.save()
    else:
        city = city_options[0]

    print city

    #TODO:
    #setup FeedInfo item
    #and also create a Source item

    cache_file = "%s.json" % city.tag
    cache_destination = os.path.join(os.path.dirname(source), cache_file)
    #keep a local copy of data we've processed...
    #this should help with subsequent calls
    #to make sure we don't need to duplicate calls to remote geolocation APIs:
    local_cache = load_json(cache_destination, create=True)
    if not local_cache.has_key('buildings'):
        local_cache['buildings'] = {}
    if not local_cache.has_key('parcels'):
        local_cache['parcels'] = {}
    
    locations = {}
    for key, value in local_cache['buildings'].items():
        locations[key] = Location(value)

    #geocoder helper:
    geo = Geo()
    
    with codecs.open(source, 'rb', encoding='utf-8') as csvfile:
        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        reader = csv.reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())

        count = 0
        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 10:
                pass
            
            address = row[1]
            print address

            if locations.has_key(address.upper()):
                location = locations[address.upper()]
            else:
                location = Location()

            #do some geocoding, as needed:
            search = "%s, Bloomington IN" % address.upper()

            for source in location.sources:
                geo.lookup(search, source, location)

            location.address_alt = search
            locations[address.upper()] = location

            #and check if a previous building object in the db exists
            #CREATE A NEW BUILDING OBJECT HERE
            #cur_building = Building()
            bldg = Building()

            #back it up for later
            local_cache['buildings'] = {}
            for key, value in locations.items():
                local_cache['buildings'][key] = value.to_dict()

            #enable this when downloading GPS coordinates...
            #the rest of the time it slows things down
            #save_json(cache_destination, local_cache)

            print

    save_results(locations, 'bloomington.tsv')

def main():
    #requires that at least one argument is passed in to the script itself
    #(through sys.argv)
    if len(sys.argv) > 1:
        helps = ['--help', 'help', '-h']
        for i in helps:
            if i in sys.argv:
                usage()
                exit()
        source = sys.argv[1]
        if len(sys.argv) > 2:
            destination = sys.argv[2]
        else:
            destination = None

        #read_csv(source, destination)
        read_csv(source)

    else:
        usage()
        exit()
        
if __name__ == '__main__':
    #main()
    read_csv('/c/clients/green_rentals/cities/bloomington/data/Bloomington_rental.csv')
