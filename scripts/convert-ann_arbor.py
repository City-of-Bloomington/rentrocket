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

available geocoders
from geopy.geocoders.bing import Bing
from geopy.geocoders.google import Google
from geopy.geocoders.googlev3 import GoogleV3
from geopy.geocoders.dot_us import GeocoderDotUS
from geopy.geocoders.geonames import GeoNames
from geopy.geocoders.wiki_gis import MediaWiki
from geopy.geocoders.wiki_semantic import SemanticMediaWiki
from geopy.geocoders.yahoo import Yahoo
from geopy.geocoders.openmapquest import OpenMapQuest
from geopy.geocoders.mapquest import MapQuest

"""

import os, sys, codecs, re
import csv

#from geopy import geocoders

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

## def save_results(locations):
##     destination = "test.tsv"
##     print "Saving: %s results to %s" % (len(locations, destination))
##     with codecs.open(destination, 'w', encoding='utf-8') as out:
##         #print locations.values()[0].make_header()
##         out.write(locations.values()[0].make_header())
##         for key, location in locations.items():
##             location.compare_points()
##             #print location.make_row()
##             out.write(location.make_row())
##     exit()
    
    
def read_csv(source):
    #for reading unicode
    #f = codecs.open(source, 'r', encoding='utf-8')

    city_options = City.objects.filter(tag="ann_arbor")
    print len(city_options)
    if not len(city_options):
        city = City()
        city.name = "Ann Arbor"
        city.tag = to_tag(city.name)
        city.save()
    else:
        city = city_options[0]

    print city

    #TODO:
    #setup FeedInfo item
    #and also create a Source item

    permit_sub_types = []
    status_types = []
    building_nums = []
    applicants = []
    managers = []

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
    
    #with open('eggs.csv', 'rb') as csvfile:
    with codecs.open(source, 'rb', encoding='utf-8') as csvfile:
        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        reader = csv.reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())

        count = 0
        for row in reader:
            count += 1
            #could exit out early here, if needed
            if count > 10:
                pass

            print row
            
            #type of building (eg: sf attached, duplex, etc)
            permit_id = row[0]

            #should always be "RENTAL" (don't need to track this one)
            permit_type = row[1]
            if not permit_type == "RENTAL" and not permit_type == "MECHANICAL":
                raise ValueError, "Unexpected permit type: %s in row: %s" % (
                    permit_type, row)
            
            sub_type = row[2]
            
            #can use this to filter out non-rental or obsolete entries
            #don't need to track otherwise:
            status = row[3]
            parcel_id = row[4]
            address = row[5]

            #should be fixed per source:
            city = row[6]
            if not ( (city.lower() == 'ann arbor') or (city == '') ):
                raise ValueError, "Unexpected city: %s" % (city)

            sqft = row[7]
            number_of_buildings = row[8]
            applicant_name = row[9]
            number_of_stories = row[10]
            number_of_units = row[11]
            
            if (not status in ['EXPIRED', 'CLOSED']) and (permit_type in ['RENTAL']):
                #check if we've started processing any results for this row
                #if local_cache['buildings'].has_key(address.upper()):
                #    local_cache_cur = local_cache['buildings'][address.upper()]
                #else:
                #    local_cache_cur = {}

                if locations.has_key(address.upper()):
                    location = locations[address.upper()]
                else:
                    location = Location()

                #do some geocoding, as needed:
                search = "%s, Ann Arbor MI" % address.upper()

                for source in location.sources:
                    geo.lookup(search, source, location)

                location.address_alt = search

                locations[address.upper()] = location

                #local_cache['buildings'][address.upper()] = local_cache_cur
                

                #and check if a previous building object in the db exists
                #CREATE A NEW BUILDING OBJECT HERE
                #cur_building = Building()
                bldg = Building()
                bldg.type = sub_type
                


            #back it up for later
            local_cache['buildings'] = {}
            for key, value in locations.items():
                local_cache['buildings'][key] = value.to_dict()
            
            save_json(cache_destination, local_cache)
            #exit()

            #THE FOLLOWING ARE FOR INFORMATIONAL PURPOSES ONLY
            #(to see what data is available)

            if not status in status_types:
                #print "adding: %s" % sub_type
                status_types.append(status)


            if not sub_type in permit_sub_types:
                #print "adding: %s" % sub_type
                permit_sub_types.append(sub_type)

            building_num = row[8]
            if not building_num in building_nums:
                #print "adding: %s" % sub_type
                building_nums.append(building_num)


            applicant = row[9]
            if ( re.search('MGMT', applicant) or
                 re.search('REALTY', applicant) or 
                 re.search('PROPERTIES', applicant) or 
                 re.search('MANAGEMENT', applicant) or 
                 re.search('GROUP', applicant) or 
                 re.search('LLC', applicant) or 
                 re.search('L.L.C.', applicant) or 
                 re.search('INC', applicant)
                 ):
                if not applicant in managers:
                    managers.append(applicant)
            else:
                if not applicant in applicants:
                    applicants.append(applicant)
            
            

            #print ', '.join(row)
            #print

    ## print permit_sub_types
    print status_types
    print building_nums

    save_results(locations)

    ## print applicants
    ## print len(applicants)
    ## print managers
    ## print len(managers)
            
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
    #read_csv('/c/clients/green_rentals/data/bloomington/Bloomington_rental.csv')
    #read_csv('/c/clients/green_rentals/data/ann_arbor/AnnArbor_RentalPermits_Export_06.25.2013.csv')
    read_csv('/c/clients/green_rentals/cities/ann_arbor/data/AnnArbor_RentalPermits_Export_06.25.2013.csv')
