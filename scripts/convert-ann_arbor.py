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

import os, sys, codecs, re
import csv

import geopy

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
from rentrocket import settings
from django.core.management import setup_environ
setup_environ(settings)

from building.models import Building, Parcel
from city.models import City

def usage():
    print __doc__
    
def read_csv(source):
    #for reading unicode
    #f = codecs.open(source, 'r', encoding='utf-8')

    city_options = City.objects.filter(tag="ann_arbor")
    print len(city_options)
    if not len(city_options):
        city = City()
        city.name = "Ann Arbor"
        city.tag = "ann_arbor"
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
    #with open('eggs.csv', 'rb') as csvfile:
    with codecs.open(source, 'rb', encoding='utf-8') as csvfile:
        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        reader = csv.reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())
        
        for row in reader:
            cur_building = Building()

            status = row[3]
            sub_type = row[2]
            if not status in ['EXPIRED', 'CLOSED']:
                bldg = Building()
                bldg.type = sub_type
                

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
    read_csv('/c/clients/green_rentals/data/ann_arbor/AnnArbor_RentalPermits_Export_06.25.2013.csv')
