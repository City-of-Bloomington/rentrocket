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
from source.models import FeedInfo, Source
from person.models import Person

def usage():
    print __doc__

conversions = { 

                }

#for storing fixes for addresses:
conversions = { "3111 S LEONARD SPRINGS RD": '',

                }


def read_csv(source_csv):
    city_options = City.objects.filter(tag="bloomington")
    print "Number of cities available: %s" % len(city_options)
    if not len(city_options):
        city = City()
        city.name = "Bloomington"
        city.tag = to_tag(city.name)
        city.save()
    else:
        city = city_options[0]

    print city

    feed_date = "2013-08-29"

    feeds = FeedInfo.objects.filter(city=city).filter(added=feed_date)
    if feeds.exists():
        feed = feeds[0]
        print "Already had feed: %s, %s" % (feed.city, feed.added)
    else:
        feed = FeedInfo()
        feed.city = city
        feed.added = feed_date
        feed.version = "0.1"
        feed.save()
        print "Created new feed: %s" % feed.city

    people = Person.objects.filter(name="Blank")
    if people.exists():
        person = people[0]
        print "Already had person: %s" % (person.name)
    else:
        person = Person()
        person.name = "Blank"
        person.save()
        print "Created new person: %s" % person.name

    sources = Source.objects.filter(feed=feed)
    if sources.exists():
        feed_source = sources[0]
        print "Already had source: %s, %s" % (feed_source.feed.city, feed_source.feed.added)
    else:
        feed_source = Source()
        feed_source.feed = feed
        feed_source.person = person
        feed_source.save()
        print "Created new source: %s" % feed_source.feed.city


    cache_file = "%s.json" % city.tag
    cache_destination = os.path.join(os.path.dirname(source_csv), cache_file)
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

    skips = 0
    with codecs.open(source_csv, 'rb', encoding='utf-8') as csvfile:
        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        reader = csv.reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())

        count = 0
        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 1000:
                #exit()
                pass
            
            address = row[1]
            print address

            bldg_id = row[0]
            print bldg_id

            if conversions.has_key(address.upper()):
                address = conversions[address.upper()]

            #make sure it's not one we're skipping:
            if not address:
                print "SKIPPING ITEM: %s" % row[1]
                skips += 1
            else:
                if locations.has_key(address.upper()):
                    location = locations[address.upper()]
                else:
                    location = Location()

                #temporarily just want to look at google again
                location.sources = ["google"]

                #do some geocoding, as needed:
                search = "%s, Bloomington IN" % address.upper()

                any_updated = False
                for geo_source in location.sources:
                    update = geo.lookup(search, geo_source, location, force=True)
                    if update:
                        any_updated = True

                location.sources = ["google", "bing", "usgeo", "geonames", "openmq", "mq"]

                if not hasattr(location, "address_alt") or not location.address_alt:
                    location.address_alt = search
                    locations[address.upper()] = location
                    any_updated = True

                match = False
                #find an address to use
                for geo_source in location.sources:
                    if not match:
                        source_list = location.get_source(geo_source)
                        if len(source_list) and source_list[0]['place'] and source_list[0]['place'] != 'Bloomington, IN, USA':
                            print "using: %s to check: %s" % (geo_source, source_list[0]['place'])
                            match = True

                            #TODO: process this a bit more...
                            #probably don't want city and zip here:
                            cur_address = source_list[0]

                            cid = "bloomington-%s" % bldg_id 

                            parcels = Parcel.objects.filter(custom_id=cid)
                            if parcels.exists():
                                parcel = parcels[0]
                                print "Already had parcel: %s" % parcel.custom_id
                            else:
                                parcel = Parcel()
                                parcel.custom_id = cid
                                parcel.save()
                                print "Created new parcel: %s" % parcel.custom_id


                            buildings = Building.objects.filter(city=city)
                            buildings.filter(address=cur_address)

                            #check if a previous building object in the db exists
                            if buildings.exists():
                                bldg = buildings[0]
                                print "Already had: %s" % bldg.address
                            else:
                                #if not, 
                                #CREATE A NEW BUILDING OBJECT HERE
                                #cur_building = Building()
                                bldg = Building()

                                bldg.address = source_list[0]['place']
                                bldg.latitude = float(source_list[0]['lat'])
                                bldg.longitude = float(source_list[0]['lng'])

                                bldg.parcel = parcel
                                bldg.geocoder = geo_source
                                bldg.source = feed_source

                                bldg.city = city

                                bldg.save()


                                print "Created new building: %s" % bldg.address
                        else:
                            print "Skipping: %s with value: %s" % (geo_source, source_list[0]['place'])
                
                if any_updated:
                    #back it up for later
                    #enable this when downloading GPS coordinates...
                    #the rest of the time it slows things down
                    local_cache['buildings'] = {}
                    for key, value in locations.items():
                        local_cache['buildings'][key] = value.to_dict()
                    save_json(cache_destination, local_cache)

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
