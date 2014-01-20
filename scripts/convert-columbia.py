#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2013.12.17 20:44:16 
# License: GPLv3

# Requires:
#
# geopy

# Description:

Columbia provides lat/long coordinates with addresses, so import should be simpler. 

"""

import os, sys, codecs, re
import csv
#import unicodecsv

from helpers import save_json, load_json, Location, Geo, save_results, make_building, make_person, make_unit

#from django.conf import settings
#settings.configure()

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
## from rentrocket import settings
## from django.core.management import setup_environ
## setup_environ(settings)

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

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


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

    feed_date = "2013-10-16"

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
    #with codecs.open(source_csv, 'rb', encoding='utf-8') as csvfile:
    with open(source_csv) as csvfile:
        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        #reader = csv.reader(csvfile)
        #reader = unicodecsv.UnicodeReader(csvfile, encoding='utf-8')

        reader = unicode_csv_reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())

        count = 0

        #want to randomize the order... distribute options more evenly
        #print len(reader)
        #exit()
        #in order to randomize, should randomize the order in the csv
        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 10:
                #exit()
                pass

            print row
            address = row[0]


            ## no_units = row[12]


            #can pass this in as bldg_id to make_building
            #that gets used for parcel too
            parcel_id = row[1]
            bldg_id = parcel_id

            street_num = row[2]
            street_dir = row[3]
            street_name = row[4]
            street_sfx = row[5]
            #eg building number
            qualifier_pre = row[6]
            #eg "UNIT" or "APT"
            qualifier_post = row[7]
            apt_num = row[8]
            #skip row9 (in/out... whatever that means)
            zip_code = row[10]
            #skip row11, assessor id
            #skip row12, address num
            #skip row13, x
            #skip row14, y
            #xcoord == lng
            lng = row[15]
            lat = row[16]

            #entry floor number: (named 'z' in sheet)
            floor = row[17]

            #skip row18, strcid... not sure
            #skip row19, parent
            #skip row20, app_
            #skip row21, hteloc
            zone = row[22]
            bldg_type = row[23]
            #number of buildings
            bldg_num = row[24]
            no_units = row[25]

            #skip row[26], inspection type
            #skip row27, app number
            #skip row28, date received
            #skip row29, application type
            #skip row30, ownerid
            #skip row31, operator id
            #skip row32, agent_id
            #skip row33, mail to
            central_heat = row[34]
            if central_heat == 'Y':
                central_heat = True
            else:
                central_heat = False

            #heat mechanism? heat mechanic??? not sure
            heat_mech = row[35]
            #skip row36, agent id (2)
            #skip row37, agent last name
            #skip row38 agent first name
            #skip row39 agent middle initial
            #skip row40, agent title
            #skip row41, business name

            #could be owner, could be agent
            owner_name = row[42]
            owner_address1 = row[43]
            owner_address2 = row[44]
            owner_city = row[45]
            owner_state = row[46]
            owner_zip = row[47]

            
            #address = " ".join([street_num, street_dir, street_name, street_sfx, qualifier_pre, qualifier_post, apt_num])

            address_main = " ".join([street_num, street_dir, street_name, street_sfx, qualifier_pre])
            address_main = address_main.strip()
            #get rid of any double spaces
            address_main = address_main.replace("  ", " ")
            
            apt_main = " ".join([qualifier_post, apt_num])
            apt_main = apt_main.strip()

            address = address_main
            print address

            owner_address = ", ".join([owner_address1, owner_address2, owner_city, owner_state, owner_zip])
            
            ## #should always be "RENTAL" (don't need to track this one)
            ## permit_type = row[1]
            ## if not permit_type == "RENTAL" and not permit_type == "MECHANICAL":
            ##     raise ValueError, "Unexpected permit type: %s in row: %s" % (
            ##         permit_type, row)
            
            ## bldg_type = row[2]
            
            ## #can use this to filter out non-rental or obsolete entries
            ## #don't need to track otherwise:
            ## status = row[3]
            ## parcel_id = row[4]

            ## #should be fixed per source:
            ## ss_city = row[6]

            ## bldg_sf = row[7]
            ## no_bldgs = row[8]
            ## applicant_name = row[9]
            ## no_stories = row[10]
            ## no_units = row[11]

            ## sqft = row[7]
            ## number_of_buildings = row[8]
            ## applicant_name = row[9]
            ## number_of_stories = row[10]
            ## number_of_units = row[11]
            
            #check if this is one we want to skip
            if conversions.has_key(address.upper()):
                address = conversions[address.upper()]

            ## if (not status in ['EXPIRED', 'CLOSED']) and (permit_type in ['RENTAL']):

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
            #location.sources = ["google"]
            #location.sources = ["google", "bing"]
            #location.sources = ["google", "bing", "usgeo", "geonames", "openmq"]
            #skip geocoding for columbia
            location.sources = []
            
            #do some geocoding, as needed:
            search = "%s, %s, %s" % (address.upper(), city_name, city.state)

            any_updated = False
            for geo_source in location.sources:
                update = geo.lookup(search, geo_source, location, force=True)
                #update = geo.lookup(search, geo_source, location, force=False)
                if update:
                    any_updated = True

            location.sources = ['csv', "google", "bing", "usgeo", "geonames", "openmq", "mq"]

            #manually add data from csv here:
            result = []
            result.append({'place': address, 'lat': lat, 'lng': lng})
            setattr(location, 'csv', result)

            #this is the case for brand new searches
            #(which are updated in a different sense)
            if not hasattr(location, "address_alt") or not location.address_alt:
                any_updated = True

            location.address_alt = search
            #location.bldg_units = bldg_units
            #location.units_bdrms = units_bdrms
            locations[address.upper()] = location

            #handle the database storage
            bldg = make_building(location, bldg_id, city, feed_source, no_units=no_units, bldg_type=bldg_type)

            if apt_main:
                unit = make_unit(apt_main, bldg)

            (person, bldg_person) = make_person(owner_name, bldg, "Agent", address=owner_address)


            if any_updated:
                #back it up for later
                #enable this when downloading GPS coordinates...
                #the rest of the time it slows things down
                local_cache['buildings'] = {}
                for key, value in locations.items():
                    local_cache['buildings'][key] = value.to_dict()
                save_json(cache_destination, local_cache)

            print

            #exit()
            
    destination = '%s.tsv' % city_tag
    save_results(locations, destination)

if __name__ == '__main__':
    #original order:
    #read_csv('/c/clients/green_rentals/cities/columbia/rental/Columbia_data_20131016.csv', "Columbia", "columbia_mo")
    read_csv('/c/clients/green_rentals/cities/columbia/rental/Columbia_data_20131016-randomized.csv', "Columbia", "columbia_mo")
