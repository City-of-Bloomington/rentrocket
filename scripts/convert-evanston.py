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

skipping:
row 1293
CHICAGO AVENUE, 1210	142808-12	10/29/12	$20.00	$20.00	11/9/12	Sent to:Patricia DeNoyer, Coldwell Banker, 2929 Central Street, Evanston, IL  60201	$0.00	ck # 0409			Rental Invoice Report - Paid	1


"""

import os, sys, codecs, re
import csv
#import unicodecsv

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

    feed_date = "2013-07-31"

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
        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 1000:
                #exit()
                pass
            
            address = row[0]

            #need to fix the number being at the end of the address
            parts = address.split(',')
            anumber = parts[-1]
            parts = parts[:-1]
            street = ",".join(parts)
            address = "%s %s" % (anumber, street)


            invoice_number = row[1]
            bldg_id = row[1]
            print bldg_id

            #this is where owner is stored
            invoice_note = row[6]
            print invoice_note
            if re.match('Sent to:', invoice_note):
                print "changing invoice note from: %s" % invoice_note
                invoice_note = invoice_note[8:]
                print "to: %s" % invoice_note
            else:
                #raise ValueError, "invoice note does not start with Sent to"
                print "!!!!!invoice note does not start with Sent to!!!!!"
                print ""
                print ""

            no_units = row[12]
            
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

            ## if not ( (ss_city.lower() == city_name.lower()) or (ss_city == '') ):
            ##     raise ValueError, "Unexpected city: %s" % (ss_city)

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
            #location.sources = ["google", "bing", "usgeo", "geonames", "openmq"]
            location.sources = ["google", "bing"]

            #do some geocoding, as needed:
            search = "%s, %s, %s" % (address.upper(), city_name, city.state)

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
            bldg = make_building(location, bldg_id, city, feed_source, no_units=no_units)

            if invoice_note:
                (person, bldg_person) = make_person(invoice_note, bldg, "Permit Applicant")

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
    read_csv('/c/clients/green_rentals/cities/evanston/data/Evanston_RentalDBExport_131016.csv', "Evanston", "evanston")
