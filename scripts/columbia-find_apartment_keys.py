#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2014.09.09 18:31:31 
# License: GPLv3

go through data and find all unique apartment identifiers

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


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def read_csv(source_csv, city_name, city_tag):

    qualifiers = []
    skips = 0
    with open(source_csv) as csvfile:
        reader = unicode_csv_reader(csvfile)

        print '>, <'.join(reader.next())

        count = 0

        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 10:
                #exit()
                pass

            #print row
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
            if not qualifier_post in qualifiers:
                qualifiers.append(qualifier_post)
            
        print qualifiers
            
    #destination = '%s.tsv' % city_tag
    #save_results(locations, destination)

if __name__ == '__main__':
    read_csv('/c/clients/rentrocket/cities/columbia/rental/Columbia_data_20131016-randomized.csv', "Columbia", "columbia_mo")
