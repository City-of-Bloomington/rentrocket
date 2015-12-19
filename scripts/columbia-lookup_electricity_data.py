#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2015.05.16 11:38:01 
# License: GPLv3

# Requires:

# Description:
This script assumes buildings and units have been created in the database

It should be possible to use the original CSV *or* the database as the main source for the addresses to look up

http://www.gocolumbiamo.com/Finance/Utilities/rental-costs.php
http://www.gocolumbiamo.com/cfforms/ub/ubmap.html
http://www.gocolumbiamo.com/cfforms/ub/rental.html
http://www.gocolumbiamo.com/cfforms/ub/ubdata.cfm?LOCID=28010&AppNum=113
http://www.gocolumbiamo.com/cfforms/ub/ubdata.cfm?LOCID=165488&AppNum=5517

requires running 
convert-columbia.py
first to make sure all buildings have been geocoded and created in database.

/c/clients/rentrocket/code/rentrocket/scripts/columbia-lookup_electricity_data.py


"""

import os, sys, codecs, re
import csv
#import unicodecsv

#not sure that urllib2 will suffice here...
#lots of javascript processing of requests on the client side..
#import urllib2
from selenium import webdriver
from time import strptime
from datetime import datetime

from django.utils import timezone
import time

from helpers import save_json, load_json, Location, save_results, make_person
#from building.models import make_building, make_unit
from building.models import lookup_building_with_geo, UTILITY_TYPES
#from rentrocket.helpers import address_search
from rentrocket.helpers import SearchResults, handle_place

from utility.models import ServiceProvider, UtilitySummary

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
                #'3603 BERKSHIRE CT': '',
                '2405 FLORIDA CT': '2405 FLORIDA',
                #works in google maps, but not here
                #'1012 COLBY DR': '1012 Colby Drive',
                '1012 COLBY DR': '',
                #'3905 ATHENS CT': '',
                #'3901 ATHENS CT': '',
                #'4000 LAMAR CT': '',
                #'3902 CAMERON CT': '',
                #'1708 PERKINS DR': '',
                #'4802 MONITEAU CT': '',
                '8 N KEENE ST BLDG E&F': '8 N KEENE ST',
                '7000 N BUCKINGHAM SQ': '7000 N BUCKINGHAM SQUARE',
                '8 N KEENE ST BLDG G&H': '8 N KEENE ST',
                '5513 HUNLEY CT': '5513 HUNLEY',
                '1804 LIGHTVIEW DR': '',
                '1704 HIGHRIDGE DR': '',
                '2211 LACLEDE DR': '', 
                '5402 GEMSTONE WAY': '',
                }

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def update_summary(query, date, cost, amount, bldg, unit, provider, utility_type, uom):
    #'electricity'
    dt = datetime(*(strptime(date, "%Y-%m-%d")[0:6]))

    #date = dt
    ## print dt
    ## print timezone.get_current_timezone()
    ## print timezone.get_default_timezone()
    ## print dir(timezone)
    #date = timezone.make_aware(dt, timezone.get_current_timezone())
    #date = timezone.make_aware(dt, timezone.get_default_timezone())
    date = timezone.make_aware(dt, timezone.utc)
    ## print date
    ## print
    
    matches = query.filter(start_date=date)
    if len(matches):
        updated = False
        summary = matches[0]
        #print "found something", summary.cost, cost, date
        if summary.cost != float(cost):
            print "Different costs:", float(cost)
            summary.cost = float(cost)
            updated = True

        if summary.amount != float(amount):
            summary.amount = float(amount)
            updated = True

        if updated:
            print "FOUND EXISTING! (and changes!)"
            summary.save()

    else:
        print date, cost, amount
        print "MAKING NEW!"

        summary = UtilitySummary()
        summary.building = bldg
        summary.unit = unit
        summary.type = utility_type

        summary.provider = provider

        summary.start_date = date
        summary.cost = float(cost)
        summary.amount = float(amount)
        summary.unit_of_measurement = uom

        summary.save()
        #print "Saving new!!"

    

def read_csv(source_csv, city_name, city_tag, driver):
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

    position_file = "position.json"
    position = load_json(position_file, create=True)
    if not position:
        position = 0

    cache_file = "%s-20150525.json.bkup" % city.tag
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

    provider = ''
    provider_options = ServiceProvider.objects.filter(name='City of Columbia')
    if len(provider_options):
        provider = provider_options[0]
    else:
        raise ValueError, "error finding utility_provider: %s matches" % len(provider_options)                    


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
            print "Looking at row: %s, position: %s" % (count, position)
            start = datetime.now()
            print "Started: ", start
            
            any_updated = False
            
            #could exit out early here, if needed
            if count > 10:
                #exit()
                pass

            #if you want to skip ahead more quickly:
            #if count < 0:
            if count < position:
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
                ## owner_name = row[42]
                ## owner_address1 = row[43]
                ## owner_address2 = row[44]
                ## owner_city = row[45]
                ## owner_state = row[46]
                ## owner_zip = row[47]


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
                if re.search('BERKSHIRE CT', address_main):
                    address_main = address_main.replace('BERKSHIRE CT', 'BERKSHIRE')
                    #address_main = ''
                if re.search('CAMERON CT', address_main):
                    address_main = address_main.replace('CAMERON CT', 'CAMERON')
                    #address_main = ''
                if re.search('ATHENS CT', address_main):
                    address_main = address_main.replace('ATHENS CT', 'ATHENS')
                    #address_main = ''
                if re.search('LAMAR CT', address_main):
                    address_main = address_main.replace('LAMAR CT', 'LAMAR')
                    #address_main = ''
                if re.search('MONITEAU CT', address_main):
                    address_main = address_main.replace('MONITEAU CT', 'MONITEAU')
                    #address_main = ''
                if re.search('IMPERIAL CT', address_main):
                    address_main = ''
                if re.search('PERKINS DR', address_main):
                    address_main = ''
                if re.search('GRANITE OAKS CT', address_main):
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


                ## if (not status in ['EXPIRED', 'CLOSED']) and (permit_type in ['RENTAL']):

                print "Parcel ID:", parcel_id
                print address

                results = None

                #make sure it's not one we're skipping:
                if not address:
                    print "SKIPPING ITEM: %s" % row[1]
                    skips += 1

                    ## skips = codecs.open("skips.txt", 'a', encoding='utf-8')
                    ## original = " ".join([street_num, street_dir, street_name, street_sfx, qualifier_pre])
                    ## skips.write(original)
                    ## skips.write('\n')
                    ## skips.close()
                    
                #check if we've started processing any results for this row
                elif not search_results.has_key(address.upper()):
                    print "No saved search results for address: %s" % address
                    print "Skipping."
                    print
                    #raise ValueError, "No results found for %s" % address

                else:
                    
                    print "Already had building: %s" % address
                    results = search_results[address.upper()]

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

                        bldg = results.building
                        assert bldg
                        unit = results.unit

                        #at this point there should be at least one unit
                        #and we will want to associate results with that unit
                        #assert unit
                        # can just pass this up in this case

                        if not unit:
                            print "Skipping address... no matching Unit!"

                        else:


                            #now that we have a building
                            #look up energy data on the remote website

                            #result = urllib2.urlopen("http://example.com/foo/bar")
                            #print result.read()

                            ## base = "http://www.gocolumbiamo.com/cfforms/ub/rental.html"
                            ## driver.get(base)
                            ## search = driver.find_element_by_css_selector('#address')
                            ## search.send_keys(address)
                            ## button = driver.find_element_by_css_selector('.ui-bar > a:nth-child(2)')
                            ## #button = driver.find_element_by_css_selector('#PrimaryCenterColumn > div > div.ui-bar-b.ui-header > div > a.ui-btn.ui-btn-corner-all.ui-shadow.ui-btn-down-b.ui-btn-up-b')
                            ## #button = driver.find_element_by_css_selector('#PrimaryCenterColumn > div > div.ui-bar-b.ui-header > div > a.ui-btn.ui-btn-corner-all.ui-shadow.ui-btn-down-b.ui-btn-up-b > span > span')
                            ## button.click()
                            ## time.sleep(4)

                            ## #results = driver.find_element_by_css_selector('.dojoxGridMasterView')
                            ## results = driver.find_element_by_css_selector('.dojoxGridContent > div:nth-child(1)')
                            ## print results.get_attribute('innerHTML')
                            ## print parcel_id

                            ## options = results.find_elements_by_tag_name('div')
                            ## #options = results.find_elements_by_link_text(parcel_id)
                            ## print options
                            ## #something didn't work with this:
                            ## #look_for = '<td tabindex="-1" role="gridcell" colspan="1" class="dojoxGridCell" idx="0" style="width:90px;">%s</td>' % parcel_id
                            ## look_for = '>%s<' % parcel_id

                            ## matches = []
                            ## for option in options:
                            ##     markup = option.get_attribute('innerHTML')
                            ##     #print markup
                            ##     if re.search(look_for, markup):
                            ##         matches.append(option)
                            ##         #print "MATCH!"

                            ## if len(matches) > 1:
                            ##     print matches
                            ##     raise ValueError, "Too many matches!"
                            ## else:
                            ##     matches[0].click()


                            #just realized that this form uses the property_id
                            #which we already have...
                            #can skip the steps above that are trying to make this link:

                            base = "http://www.gocolumbiamo.com/cfforms/ub/ubdata.cfm?LOCID=%s&AppNum=79" % parcel_id
                            driver.get(base)

                            try:
                                heat_source = driver.find_element_by_css_selector('#PrimaryCenterColumn > table:nth-child(1) > tbody:nth-child(1) > tr:nth-child(3) > td:nth-child(1) > strong:nth-child(1) > font:nth-child(1)')
                                if heat_source.text.strip() == "Heating Source: Gas Heat":
                                    bldg.heat_source_details = 'gas'
                                    bldg.save()
                                else:
                                    print heat_source.text
                                    exit()
                                    #TODO:
                                    bldg.heat_source_details = 'electric'
                                    bldg.who_pays_gas = 'not_available'
                            except:
                                print "heat source not found... skipping"
                                    
                            try:
                                selector = driver.find_element_by_css_selector('#el_table_length > label:nth-child(1) > select:nth-child(1) > option:nth-child(3)')
                                selector.click()
                            except:
                                print "No Water data available... skipping"
                            else:

                                body = driver.find_element_by_css_selector('#el_table > tbody:nth-child(3)')
                                rows = body.find_elements_by_tag_name('tr')
                                #row = rows[0]
                                query = bldg.utilitysummary_set.filter(type='electricity')
                                for row in rows:
                                    #print row.get_attribute('innerHTML')
                                    cols = row.find_elements_by_tag_name('td')
                                    date = cols[0].text + '-01'
                                    cost = cols[1].text.replace('$', '').strip()
                                    amount = cols[2].text
                                    amount = amount.replace(' KWH', '')
                                    update_summary(query, date, cost, amount, bldg, unit, provider, 'electricity', 'kwh')
                                    #update_summary(query, date, cost, amount)
                                    #for item in cols:
                                    #    print item.text


                            #print dir(bldg)
                            #print bldg.utilitysummary_set
                            #query = bldg.utilitysummary_set.filter(type=utility_type[0])
                            #could look up type from UTILITY_TYPES...
                            #but in this case we know what they should be
                            #query = bldg.utilitysummary_set.filter(type='water')
                            #if len(query):

                            try:
                                water = driver.find_element_by_css_selector('#ext-gen23')
                                water.click()

                                selector = driver.find_element_by_css_selector('#wr_table_length > label:nth-child(1) > select:nth-child(1) > option:nth-child(3)')
                                selector.click()
                            except:
                                print "No Water data available... skipping"
                            else:

                                body = driver.find_element_by_css_selector('#wr_table > tbody:nth-child(3)')

                                rows = body.find_elements_by_tag_name('tr')
                                #row = rows[0]
                                query = bldg.utilitysummary_set.filter(type='water')
                                for row in rows:
                                    #print row.get_attribute('innerHTML')
                                    cols = row.find_elements_by_tag_name('td')
                                    date = cols[0].text + '-01'
                                    cost = cols[1].text.replace('$', '').strip()
                                    amount = cols[2].text
                                    amount = amount.replace(' CCF', '')
                                    update_summary(query, date, cost, amount, bldg, unit, provider, 'water', 'ccf')
                                    #update_summary(query, date, cost, amount)
                                    #for item in cols:
                                    #    print item.text


                            unit.update_averages()

                            #see if we have enough info now to make a score:
                            unit.update_energy_score()

                            #now that we've saved the unit,
                            #update the averages for the whole building:
                            unit.building.update_utility_averages()
                            unit.building.update_rent_details()

                
                position += 1
                save_json(position_file, position)
        
            if any_updated:
                #back it up for later
                #enable this when downloading GPS coordinates...
                #the rest of the time it slows things down
                local_cache['buildings'] = {}
                for key, value in search_results.items():
                    #search_results[key] = SearchResults().from_dict(value)
                    local_cache['buildings'][key] = value.to_dict()
                save_json(cache_destination, local_cache)

                position = count
                save_json(position_file, position)
                exit()

            end = datetime.now()
            print "finished: ", end
            total_time = end - start
            print total_time

            print

            #exit()
            
    #destination = '%s.tsv' % city_tag
    #save_results(search_results, destination)

if __name__ == '__main__':
    driver = webdriver.Firefox()
    #driver = webdriver.Chrome()

    read_csv('/home/rentrocket/cities/columbia/rental/Columbia_data_20131016-randomized.csv', "Columbia", "columbia_mo", driver)
