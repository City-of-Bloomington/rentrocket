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

from helpers import save_json, load_json, Location, Geo, save_results, make_building, make_person

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
from rentrocket import settings
from django.core.management import setup_environ
setup_environ(settings)

from city.models import City, to_tag
from source.models import FeedInfo, Source
from person.models import Person

def usage():
    print __doc__

conversions = { 

                }

#for storing fixes for addresses:
conversions = {
    
                }


def read_csv(source_csv, city_name, city_tag):
    city_options = City.objects.filter(tag=city_tag)
    print "Number of cities available: %s" % len(city_options)
    if not len(city_options):
        raise ValueError, "CITY NOT FOUND! run make_cities.py first"
        ## city = City()
        ## city.name = city_name
        ## city.tag = to_tag(city.name)
        ## city.save()
    else:
        city = city_options[0]

    print city

    feed_date = "2013-09-10"

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
        print "Created new feed: %s" % feed.city.name

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
        print "Created new source: %s" % feed_source.feed.city.name


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
            
            #type of building (eg: sf attached, duplex, etc)
            permit_id = row[0]
            bldg_id = row[0]
            print bldg_id


            #should always be "RENTAL" (don't need to track this one)
            permit_type = row[1]
            if not permit_type == "RENTAL" and not permit_type == "MECHANICAL":
                raise ValueError, "Unexpected permit type: %s in row: %s" % (
                    permit_type, row)
            
            bldg_type = row[2]
            
            #can use this to filter out non-rental or obsolete entries
            #don't need to track otherwise:
            status = row[3]
            parcel_id = row[4]
            address = row[5]

            #should be fixed per source:
            ss_city = row[6]

            bldg_sf = row[7]
            no_bldgs = row[8]
            applicant_name = row[9]
            no_stories = row[10]
            no_units = row[11]
            if not ( (ss_city.lower() == city_name.lower()) or (ss_city == '') ):
                raise ValueError, "Unexpected city: %s" % (ss_city)

            sqft = row[7]
            number_of_buildings = row[8]
            applicant_name = row[9]
            number_of_stories = row[10]
            number_of_units = row[11]
            
            #check if this is one we want to skip
            if conversions.has_key(address.upper()):
                address = conversions[address.upper()]

            if (not status in ['EXPIRED', 'CLOSED']) and (permit_type in ['RENTAL']):

                #make sure it's not one we're skipping:
                if not address:
                    print "SKIPPING ITEM: %s" % row[1]
                    skips += 1
                else:
                    #check if we've started processing any results for this row
                    if locations.has_key(address.upper()):
                        location = locations[address.upper()]
                    else:
                        location = Location()

                #temporarily just want to look at google again
                location.sources = ["google"]
                #location.sources = ["google", "bing", "usgeo", "geonames", "openmq"]


                #do some geocoding, as needed:
                search = "%s, %s %s" % (address.upper(), city_name, city.state)

                any_updated = False
                for geo_source in location.sources:
                    update = geo.lookup(search, geo_source, location, force=True)
                    #update = geo.lookup(search, geo_source, location, force=False)
                    if update:
                        any_updated = True

                location.sources = ["google", "bing", "usgeo", "geonames", "openmq", "mq"]

                #this is the case for brand new searches
                #(which are updated in a different sense)
                if not hasattr(location, "address_alt") or not location.address_alt:
                    any_updated = True

                location.address_alt = search
                #location.bldg_units = bldg_units
                #location.units_bdrms = units_bdrms
                locations[address.upper()] = location

                #handle the database storage
                bldg = make_building(location, bldg_id, city, feed_source, parcel_id, bldg_type, no_units, bldg_sf)

                if applicant_name:
                    (person, bldg_person) = make_person(applicant_name, bldg, "Permit Applicant")
                
                if any_updated:
                    #back it up for later
                    #enable this when downloading GPS coordinates...
                    #the rest of the time it slows things down
                    local_cache['buildings'] = {}
                    for key, value in locations.items():
                        local_cache['buildings'][key] = value.to_dict()
                    save_json(cache_destination, local_cache)

                print

    destination = '%s.tsv' % city_tag
    save_results(locations, destination)

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
    read_csv('/c/clients/green_rentals/cities/ann_arbor/data/AnnArbor_RentalPermits_Export_06.25.2013.csv', "Ann Arbor", "ann_arbor")
