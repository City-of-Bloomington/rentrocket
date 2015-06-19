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

import os, sys, codecs, re, time
import csv
#import unicodecsv

from helpers import save_json, load_json, Location, Geo, save_results, make_person
#from building.models import make_building, make_unit
from building.models import lookup_building_with_geo
from rentrocket.helpers import SearchResults, handle_place, address_search

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


#for storing fixes for addresses:
conversions = { '101 HOLLY RIDGE LN': '101 HOLLYRIDGE LN',
                '4200 MERCHANT ST': '4200 MERCHANT STREET',
                '3603 BERKSHIRE CT': '',
                #works in google maps, but not here
                #'1012 COLBY DR': '1012 Colby Drive',
                '1012 COLBY DR': '',
                #'3905 ATHENS CT': '',
                '5402 GEMSTONE WAY': '',
                '4802 MONITEAU CT': '',
                #'4000 LAMAR CT': '',
                '5513 HUNLEY CT': '',
                #'3902 CAMERON CT': '',
                '8 N KEENE ST BLDG E&F': '8 N KEENE ST',
                '7000 N BUCKINGHAM SQ': '7000 N BUCKINGHAM SQUARE',
                #'1708 PERKINS DR': '',
                #'3901 ATHENS CT': '',
                '1804 LIGHTVIEW DR': '',
                '8 N KEENE ST BLDG G&H': '8 N KEENE ST',
                '1704 HIGHRIDGE DR': '',
                '2211 LACLEDE DR': '', 
                '2405 FLORIDA CT': '',
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


    cache_file = "%s-20150525.json" % city.tag
    cache_destination = os.path.join(os.path.dirname(source_csv), cache_file)
    #keep a local copy of data we've processed...
    #this should help with subsequent calls
    #to make sure we don't need to duplicate calls to remote geolocation APIs:
    local_cache = load_json(cache_destination, create=True)
    if not local_cache.has_key('buildings'):
        local_cache['buildings'] = {}
    
    search_results = {}
    for key, value in local_cache['buildings'].items():
        #search_results[key] = Location(value)
        sr = SearchResults()
        sr.from_dict(value)
        #print
        #print sr
        #print 
        search_results[key] = sr

    #geocoder helper:
    #geo = Geo()

    skips = 0
    with open(source_csv) as csvfile:

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

            any_updated = False
            
            #could exit out early here, if needed
            if count > 10:
                #exit()
                pass

            #if you want to skip ahead more quickly:
            if count < 26799:
                pass
            else:

                #print row
                objectid = row[0]


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

                #this is causing problems with lookups in google
                if qualifier_pre == "DUP" or qualifier_pre == "DUPE" or qualifier_pre == "2-Jan" or qualifier_pre == "HM" or qualifier_pre == "DWN":
                    qualifier_pre = ''

                address_main = " ".join([street_num, street_dir, street_name, street_sfx, qualifier_pre])
                address_main = address_main.strip()
                #get rid of any double spaces
                address_main = address_main.replace("  ", " ")

                #similar to conversions,
                #but there are too many of these to list there
                if re.search('HOLLY RIDGE LN', address_main):
                    address_main = address_main.replace('HOLLY RIDGE LN', 'HOLLYRIDGE LN')
                if re.search('BERKSHIRE', address_main):
                    address_main = ''
                if re.search('IMPERIAL CT', address_main):
                    address_main = ''
                if re.search('MONITEAU CT', address_main):
                    address_main = ''
                if re.search('LAMAR CT', address_main):
                    address_main = ''
                if re.search('CAMERON CT', address_main):
                    address_main = ''
                if re.search('PERKINS DR', address_main):
                    address_main = ''
                if re.search('GRANITE OAKS CT', address_main):
                    address_main = ''
                if re.search('ATHENS CT', address_main):
                    address_main = ''
                    

                #sometimes the 'BLDG' data is added in the wrong place
                #then it gets treated as a unit item
                #(but it's not *always* a unit item, so can't generalize it that way)
                if qualifier_post == "BLDG" or qualifier_post == "LOT":
                    address_main = " ".join([address_main, qualifier_post, apt_main])
                    address_main = address_main.strip()
                    apt_main = ''
                else:
                    apt_main = " ".join([qualifier_post, apt_num])
                    apt_main = apt_main.strip()

                #check if this is one we want to skip
                if conversions.has_key(address_main.upper()):
                    address_main = conversions[address_main.upper()]

                if address_main:
                    print "APT_MAIN: ", apt_main
                    address = ", ".join( [address_main, apt_main] )
                else:
                    address = ''

                owner_address = ", ".join([owner_address1, owner_address2, owner_city, owner_state, owner_zip])


                ## if (not status in ['EXPIRED', 'CLOSED']) and (permit_type in ['RENTAL']):

                print "Parcel ID:", parcel_id
                print address



                results = None

                #make sure it's not one we're skipping:
                if not address:
                    print "SKIPPING ITEM: %s" % row[1]
                    skips += 1

                    skipf = codecs.open("skips.txt", 'a', encoding='utf-8')
                    original = " ".join([street_num, street_dir, street_name, street_sfx, qualifier_pre])
                    skipf.write(original)
                    skipf.write('\n')
                    skipf.close()

                else:
                    #check if we've started processing any results for this row
                    if search_results.has_key(address.upper()):
                        print "Already had building: %s" % address
                        results = search_results[address.upper()]
                        #print results
                    else:

                        addy = ", ".join( [address_main, city.name, city.state] )
                        addy += " " + zip_code
                        #addy += ", USA"
                        print addy

                        #toggle betweeen an actual google query
                        results = address_search(addy, apt_main)

                        #print dir(results)

                        if len(results.matches) > 1:
                            print results
                            for option in results.matches:
                                print "%s: %s, %s" % (option['place'], option['lat'], option['lng'])
                            print
                            print "Source Lat: %s, Lng: %s" % (lat, lng)
                            src_lat = int(float(lat) * 100) 
                            src_lng = int(float(lng) * 100)

                            matched = False
                            for current in results.matches:
                                #current = results.matches[0]
                                print current['lat']
                                print current['lng']
                                #only want to look at the first 2 decimal places:
                                comp_lat = int(float(current['lat']) * 100) 
                                comp_lng = int(float(current['lng']) * 100)
                                print comp_lat
                                print comp_lng

                                if (src_lat == comp_lat) and (src_lng == comp_lng):
                                    #results.matches = results.matches[:1]
                                    results.matches = [ current ]
                                    matched = True

                            if not matched:
                                print "DIDN'T MATCH!"
                                exit()                            

                        any_updated = True

                        # or just using results as specified in csv
                        # (THIS DOES NOT NORMALIZE THE ADDRESS VIA GOOGLE)
                        #results = SearchResults()
                        #results.unit_text = apt_main
                        #handle_place(results, addy, lat, lng, apt_main)


                    assert results
                    #print results

                    lookup_building_with_geo(results, make=True, parcel_id=parcel_id)
                    #print results
                    #current['results'] = results

                    #print results

                    if results.errors:
                        print results
                        raise ValueError, results.errors
                    else:

                        search_results[address.upper()] = results

                        bldg = results.building
                        assert bldg
                        unit = results.unit

                        # may be a case where the unit is blank
                        # and another unit with an number/letter was created earlier
                        # in that case, we won't be creating one here
                        # and the building will already exist...
                        # not necessarily an error though
                        # just redundant data
                        #assert unit

                        (person, bldg_person) = make_person(owner_name, bldg, "Agent", address=owner_address)

                    time.sleep(1)
            

            if any_updated:
                #back it up for later
                #enable this when downloading GPS coordinates...
                #the rest of the time it slows things down
                local_cache['buildings'] = {}
                for key, value in search_results.items():
                    #search_results[key] = SearchResults().from_dict(value)
                    local_cache['buildings'][key] = value.to_dict()
                save_json(cache_destination, local_cache)

            print

            #exit()
            
    #destination = '%s.tsv' % city_tag
    #save_results(search_results, destination)

if __name__ == '__main__':
    #original order:
    #read_csv('/c/clients/green_rentals/cities/columbia/rental/Columbia_data_20131016.csv', "Columbia", "columbia_mo")
    read_csv('/c/clients/rentrocket/cities/columbia/rental/Columbia_data_20131016-randomized.csv', "Columbia", "columbia_mo")
