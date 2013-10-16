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

from helpers import save_json, load_json, Location, Geo, save_results, make_building, make_person, parse_person

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

def special_cases(text):
    #these are not parsed correctly due to numbers in the names,
    #or no numbers in the address
    #manually fixing here:
    options = {
        "14th & College Holdings, Llc, 807 N. Walnut St, Bloomington, IN 47404": ("14th & College Holdings, Llc", "807 N. Walnut St, Bloomington, IN 47404"),
        "926 West 2nd Llc, 910 South Rogers St, Bloomington, IN 47403": ("926 West 2nd Llc", "910 South Rogers St, Bloomington, IN 47403"),
        "16th & Dunn Holdings, Llc, 1128 S. College Mall Road, Bloomington, IN 47401": ("16th & Dunn Holdings, Llc", "1128 S. College Mall Road, Bloomington, IN 47401"),
        "916 South Rogers Llc, 910 S. Rogers Street, Bloomington, IN 47403": ("916 South Rogers Llc", "910 S. Rogers Street, Bloomington, IN 47403"),
        "Toney, Kenneth & Susan, , Bloomington, IN": ("Toney, Kenneth & Susan", "Bloomington, IN"),
        "Lee, Young Soon, , South Korea, Park, Hong Bae, , South Korea": ("Lee, Young Soon & Park, Hong Bae", "South Korea"),
        "10-29 Llc, 7788 N Stinesville Rd., Gosport, IN 47433": ("10-29 Llc", "7788 N Stinesville Rd., Gosport, IN 47433"),
        "349 S. College, Llc, 345 S. College Ave. #103, Bloomington, IN 47403": ("349 S. College, Llc", "345 S. College Ave. #103, Bloomington, IN 47403"),
        "900 W. 3rd Street Llc, 910 S. Rogers Street, Bloomington, IN 47403": ("900 W. 3rd Street Llc", "910 S. Rogers Street, Bloomington, IN 47403"),
        "606 Building Company, 1149 Linden Drive, Bloomington, IN 47408": ("606 Building Company", "1149 Linden Drive, Bloomington, IN 47408"),
        "Salazar, Julio, , Bogota,Columbia": ("Salazar, Julio", "Bogota,Columbia"),
        "711 Holding Company, 44 S. Franklin Street, Bloomfield, IN 47424": ("711 Holding Company", "44 S. Franklin Street, Bloomfield, IN 47424"),
        "317 West 16th Llc, 910 S. Rogers Street, Bloomington, IN 47403": ("317 West 16th Llc", "910 S. Rogers Street, Bloomington, IN 47403"),
        "2nd And Fess, Llc, 300 N. Meridian St. Ste. 1100, Indianapolis, IN 46204": ("2nd And Fess, Llc", "300 N. Meridian St. Ste. 1100, Indianapolis, IN 46204"),
        "1st Amended Alex & Marta Liberman Revocable Trust, 20277 Via Sansovino, Porter Ranch, CA 91326": ("1st Amended Alex & Marta Liberman Revocable Trust", "20277 Via Sansovino, Porter Ranch, CA 91326"), 

        }

    if options.has_key(text):
        return options[text]
    else:
        return None

    
conversions = { 

                }

#for storing fixes for addresses:
conversions = { "3111 S LEONARD SPRINGS RD": '',
                #otherwise, this gets coded as:
                #140 Willis Street, De Kalb, MO 64440, USA
                "1600 N Willis Lot 140 ST": "1600 N Willis ST, Lot 140",
                }


def read_csv(source_csv):
    city_options = City.objects.filter(tag="bloomington")
    print "Number of cities available: %s" % len(city_options)
    if not len(city_options):
        raise ValueError, "CITY NOT FOUND! run make_cities.py first"
        ## city = City()
        ## city.name = "Bloomington"
        ## city.tag = to_tag(city.name)
        ## city.save()
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
            
            bldg_id = row[0]
            print bldg_id

            address = row[1]
            print address

            owner = row[2]

            #skip this:
            ownder_contact = row[3]

            agent = row[4]

            bldg_units = row[9]
            print bldg_units

            units_bdrms = row[10]
            print units_bdrms

            #check if this is one we want to skip
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
                    any_updated = True

                location.address_alt = search
                location.bldg_units = bldg_units
                location.units_bdrms = units_bdrms
                locations[address.upper()] = location

                #handle the database storage
                bldg = make_building(location, bldg_id, city, feed_source)

                #owner_details = parse_person(owner)
                if owner:
                    result = special_cases(owner)
                    if result:
                        (owner_name, owner_address) = result
                    else:
                        (owner_name, owner_address, owner_phone, remainder) = parse_person(owner)
                        ## print "owner name: %s" % owner_name
                        ## print "owner address: %s" % owner_address
                        ## print ""

                        if owner_name:
                            (person, bldg_person) = make_person(owner_name, bldg, "Owner", address=owner_address)

                if agent and agent != "No Agent":
                    #agent_details = parse_person(agent)
                    (agent_name, agent_address, agent_phone, remainder) = parse_person(agent)
                    ## print "agent name: %s" % agent_name
                    ## print "agent address: %s" % agent_address
                    ## print ""

                    if agent_name:
                        (person, bldg_person) = make_person(agent_name, bldg, "Agent", address=agent_address, city=city)                

                
                if any_updated:
                    #back it up for later
                    #enable this when downloading GPS coordinates...
                    #the rest of the time it slows things down
                    local_cache['buildings'] = {}
                    for key, value in locations.items():
                        local_cache['buildings'][key] = value.to_dict()
                    save_json(cache_destination, local_cache)

                print

    save_results(locations, 'bloomington-filtered.tsv')

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
