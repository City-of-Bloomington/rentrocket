#!/usr/bin/env python
"""
#
# By: Charles Brandt [code at charlesbrandt dot com]
# On: *2014.11.07 16:34:19 
# License: GPLv3

# Requires:
#
# geopy

# Description:

similiar to other convert scripts
however, this one utilized the master template format
this should be more comprehensive, and ultimately, more standard too.

utilize as much functionality from the site codebase as possible for adding data

WARNING:
be very careful if terminating this script early...
if the script is in the middle of saving the cached data to the local json file
it can result in a corrupt file
be sure to back up the json data regularly
"""

import os, sys, codecs, re, copy
import csv
#import unicodecsv

#from helpers import save_json, load_json, Location, Geo, save_results, make_building, make_person, make_unit

from helpers import save_json, load_json, make_person

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
from rentrocket.helpers import address_search, SearchResults
from building.models import lookup_building_with_geo, Building
from building.views import BuildingForm

def usage():
    print __doc__



#for storing fixes for addresses:
conversions = {
    '220 E State Road 45 46 BYP':'220 Indiana 45 46 Bypass', 
    
                }


def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]

def check_boolean(value):
    """
    often see 'yes' or 'no' values in spread sheet
    change to boolean
    """
    clean = None
    low = value.lower()
    if low == "yes":
        clean = True
    elif low == "no":
        clean = False

    elif low == 'some exceptions':
        clean = True
    

    elif value:
        raise ValueError, "No boolean matched in: %s" % value
    
    else:
        #must be empty, just return false for empty values
        clean = False

    return clean
    
def check_number(value):
    """
    for some values (costs) there are extra commas and '$'
    get rid of those

    also sometimes a - for a range...
    no room for that in the system
    just use the highest value
    """
    value = value.replace('N/A', '')
    value = value.replace('n/a', '')
    value = value.replace('Studio', '0')
    value = value.replace('studio', '0')
    value = value.replace('STUDIO', '0')
    value = value.replace(',', '')
    value = value.replace('$', '')
    value = value.replace('+', '')
    parts = value.split('-')
    value = parts[-1]
    value = value.strip()
    return value
            
def check_choices(choices, value):
    """
    go through all choices, look for a match in the value
    keep the equivalent choice value
    remove the match from original value
    """
    #making everything lower case will make life easier...
    #will cause unknown options to be lower case too...
    #this seems acceptable
    
    value = value.lower()
    clean = []
    for choice in choices:
        cur_choice = choice[1].lower()
        regex = cur_choice.replace('(', '\(')
        regex = regex.replace(')', '\)')
        regex = regex.lower()
        if re.search(regex, value):
            if not choice[0] in clean:
                clean.append(choice[0])
            value = value.replace(cur_choice, '')

    #don't need to include 'N/A' values
    #upper case shouldn't matter if converting value string to lower
    #value = value.replace('N/A', '')
    value = value.replace('n/a', '')

    #clean value... don't want to end up with a bunch of ,
    new_parts = []
    parts = value.split(',')
    for part in parts:
        current = part.strip()
        if current:
            new_parts.append(current)
    value = ",".join(new_parts)

    return clean, value

def check_who_pays(value, choices):
    """
    very similar to check_choices
    but need to have some custom checks that won't apply there:
    """
    #in this case a 'N/A' will be used to signal
    #that the service is not_available (one of the valid options for who pays)
    #get that first, before check_choices clears it out (default action)    
    more_choices = ( ('not_available', 'n/a'), )
    #TODO:
    #if all values are set to 'not_available', that probably means something
    #different than one specific service not being available in a location
    #in that case, leave the data blank
    value = value.lower()
    clean = []
    for choice in more_choices:
        #print choice
        cur_choice = choice[1].lower()
        regex = cur_choice
        #just be sure more choices is a list of lists (or tuple of tuples)
        #regex = regex.replace('/', '\/')
        #regex = '(n//a)'
        #regex = 'n\Sa+'
        #print "searching for %s in %s" % (regex, value)
        if re.search(regex, value):
            #print "matched!"
            if not choice[0] in clean:
                clean.append(choice[0])
            value = value.replace(cur_choice, '')    
    
    clean2, value = check_choices(choices, value)
    clean.extend(clean2)
    more_choices = ( ('landlord', 'Landlord (incl. in rent)'),
                     ('landlord', 'Landlrd (incl. in rent)'),
                     ('tenant', 'Tenant'),
                     ('tenant', 'tenant'),
                     )
    clean2, value = check_choices(more_choices, value)
    #add anything else in:
    clean.extend(clean2)

    return clean, value

def save_results(cache_destination, local_cache):
    #destination = '%s.tsv' % city_tag
    #save_results(locations, destination)

    #convert all results to json serializable
    for_saving = {}
    for key in local_cache.keys():
        current = local_cache[key]
        results = current['results']
        dupe = copy.copy(current)
        dupe['results'] = results.to_dict()

        for_saving[key] = dupe
        
    save_json(cache_destination, for_saving)
    
def all_done(cache_destination, local_cache):
    save_results(cache_destination, local_cache)
    exit()

def process_row(current, row, keys, local_cache, city, feed_source, count):
    """
    work on adding all of the details from one row
    to the matching building address
    """

    #print row
    for index, key in enumerate(keys):
        current[key] = row[index]

    #print current

    results = None

    address = current['street_address']
    #if unit is in second column, need it here...
    #otherwise everything gets over-written for address in local_cache:
    if current['unit_if_applicable']:
        address = ', '.join( [address, current['unit_if_applicable']] )
        
    if conversions.has_key(address):
        address = conversions[address]
        print "Using manually fixed address: %s" % address

    if address in local_cache.keys():
        print "local_cache matched ", address
        previous = local_cache[address]
        #print previous
        results = previous['results']

        #should have already been set when loading local_cache above:
        #now load it as an actual SearchResults object
        #results = SearchResults()
        #print "found matching results: %s" % results

    else:
        #do the search for the first time

        #get rid of any '*' characters...
        #these are not really part of the address:
        addy = address.replace('*', '')
        addy = addy.strip()

        #seeing units in street address with no '#' or other prefix
        #but it is separated by a comma...
        #extract that here and add a prefix (and leave out ',')
        parts = addy.split(',')
        unit = ''
        if len(parts) > 1:
            #treat last part as a unit
            unit = parts[-1].strip()
            addy = ",".join(parts[:-1]).strip()

            #check if we have both current['unit_if_applicable']
            #and found unit
            if unit and current['unit_if_applicable']:
                if unit != current['unit_if_applicable']:
                    raise ValueError, "Found both unit: %s and unit from spreadsheet: %s" % (unit, current['unit_if_applicable'])
                #otherwise it should be ok...
                #adding in unit_if_available earlier now
        else:
            unit = current['unit_if_applicable']

        #also need to add in city, state, here to help limit matches
        addy = ", ".join( [addy, city.name, city.state] )
        print addy

        results = address_search(addy, unit)

    assert results

    lookup_building_with_geo(results, make=True)
    #print results
    current['results'] = results

    print results

    if results.errors:
        #print results
        #raise ValueError, results.errors
        skips = codecs.open("skips.txt", 'a', encoding='utf-8')
        skips.write(address)
        skips.write('\n')
        skips.close()
    else:

        bldg = results.building
        assert bldg
        unit = results.unit
        assert unit


        #not sure that the building form is going to save very much effort
        #still need to customize validation
        #skipping for now
        ## buildingform = BuildingForm(instance=bldg)
        ## print dir(buildingform)
        ## print buildingform.fields.keys()

        #this would come at the end, if using form:
        #setattr(buildingform, model_attribute, value)
        #buildingform.fields[model_attribute].initial = value
        ## #use form validation to make sure no errors are missed
        ## if buildingform.is_valid():
        ##     updated = buildingform.save(commit=True)
        ## else:
        ##     print buildingform.errors
        ##     print buildingform._errors
        ##     for field in buildingform:
        ##         print dir(field)
        ##         print field.errors
        ##     print "ERRORS!"


        #Now update the unit and building details as necessary:
        #building
        bldg_map = { "unit_type":"type", "laundry":"laundry", "parking":"parking_options", "pets":"pets", "gym_fitness_center":"gym", "game_room_rec_center_community_center":"game_room", "pool":"pool", "other_amenities":"amenities", "bike_friendly":"bike_friendly_details", "recycling":"recycling", "composting":"composting", "gardening":"garden_details", "public_transit":"transit_friendly_details", "walk_friendly":"walk_friendly_details", "other_smartliving_features":"energy_saving_details", "air_conditioning":"air_conditioning", "energy_saving_features":"energy_saving_other" }
        #bldg_map = { "laundry":"laundry", "bike_friendly":"bike_friendly" }

        #now use the keys
        for sk, model_attribute in bldg_map.items():
            #have already converted to a dict
            #row_index = keys.index(spreadsheet)
            #value = row
            value = current[sk]
            clean = []

            #now need to do any field specific conversions...
            #this boils down to massive case statement
            #(but only for those that actually need it)
            #values set on the model will get automatically converted
            if sk == "laundry":
                (clean, rest) = check_choices(bldg.LAUNDRY_CHOICES, value)
                if re.search('W/D incl\. in unit', rest):
                    rest = rest.replace('W/D incl. in unit', '')
                    clean.append('in_unit')
                #print clean
                #print rest
                value = ','.join(clean)

            if sk == "air_conditioning":
                (clean, rest) = check_choices(bldg.AC_CHOICES, value)
                #print clean
                #print rest
                value = ','.join(clean)

            if sk == "recycling":
                value = check_boolean(value)

            if sk == "pets":
                value = check_boolean(value)

            if sk == "unit_type":
                (clean, rest) = check_choices(bldg.TYPE_CHOICES, value)
                #print clean
                #print rest
                #should only have one building type!
                value = ','.join(clean)

            if sk == "bike_friendly":
                (clean, rest) = check_choices(bldg.BIKE_CHOICES, value)
                #print clean
                #print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    bldg.bike_friendly_other = rest

            if sk == "public_transit":
                (clean, rest) = check_choices(bldg.TRANSIT_CHOICES, value)
                print clean
                print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    bldg.transit_friendly_other = rest

            if sk == "parking":
                print value
                (clean, rest) = check_choices(bldg.PARKING_CHOICES, value)
                print clean
                print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    #bldg.transit_friendly_other = rest
                    raise ValueError, "Unknown parking option: %s" % rest

            if sk == "other_smartliving_features":
                (clean, rest) = check_choices(bldg.ENERGY_SAVING_CHOICES, value)
                #print clean
                #print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    bldg.energy_saving_other = rest

            if sk == "energy_saving_features":
                #this values shows up here in the spreadsheet
                #that is incorrect... bad data...
                #this is a fix for that
                if "Near Bus Route" == value:
                    #multiselectfield returns a list automatically:
                    #cur_values = bldg.transit_friendly_details.split()
                    cur_values = bldg.transit_friendly_details
                    if not 'access' in cur_values:
                        print "Adding access to transit friendly details"
                        cur_values.append('access')
                    #total = ','.join(cur_values)
                    #bldg.transit_friendly_details = total
                    bldg.transit_friendly_details = cur_values

                (clean, rest) = check_choices(bldg.ENERGY_SAVING_CHOICES, value)
                #print clean
                #print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    #might loose some data here if both other_smartliving_features and this are set with different data
                    bldg.energy_saving_other = rest                    

            if sk == "gardening":
                (clean, rest) = check_choices(bldg.GARDEN_CHOICES, value)
                #print clean
                #print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    bldg.garden_other = rest

            if sk == "walk_friendly":
                (clean, rest) = check_choices(bldg.WALK_CHOICES, value)
                print clean
                print rest
                #value = ','.join(clean)
                value = clean
                if rest:
                    bldg.walk_friendly_other = rest

            if sk == "gym_fitness_center":
                value = check_boolean(value)
            if sk == "pool":
                value = check_boolean(value)
            if sk == "game_room_rec_center_community_center":
                value = check_boolean(value)

            print "Setting %s (currently: %s) to: %s" % (model_attribute, getattr(bldg, model_attribute), value)
            setattr(bldg, model_attribute, value)

            #update values based on anything that was added here
            bldg.set_booleans()

        who_pays = { "who_pays_for_electricity":"who_pays_electricity", "who_pays_for_natural_gas":"who_pays_gas", "who_pays_for_water":"who_pays_water", "who_pays_for_trash_recycling_pickup":"who_pays_trash", "who_pays_for_cable":"who_pays_cable", "who_pays_for_internet":"who_pays_internet", }

        for sk, model_attribute in who_pays.items():
            value = current[sk]
            (value, rest) = check_who_pays(value, bldg.WHO_PAYS_CHOICES)
            #print current[sk]
            #print rest
            if rest:
                raise ValueError, "Unknown who pays value: %s" % value

            print "Setting %s (currently: %s) to: %s" % (model_attribute, getattr(bldg, model_attribute), value)
            setattr(bldg, model_attribute, value)

        #unit:
        numbers = {"rent":"rent", "security_deposit":"deposit", "sq_feet_per_unit":"sqft", "num_bedrooms":"bedrooms", "num_bathrooms":"bathrooms", "maximum_occupancy_per_unit":"max_occupants", "electric_utility_cost_average_per_mo":"average_electricity", "electric_utility_cost_low":"electricity_min", "electric_utility_cost_high":"electricity_max", "natural_gas_utility_cost_average_per_mo":"average_gas", "natural_gas_utility_cost_low":"gas_min", "natural_gas_utility_cost_high":"gas_max", }

        for sk, model_attribute in numbers.items():
            value = current[sk]
            clean = []

            value = check_number(value)
            #print value
            #print clean
            #print rest
            #if rest:
            #    raise ValueError, "Unknown who pays value: %s" % value

            if value:
                print "Setting %s (currently: %s) to: %s" % (model_attribute, getattr(unit, model_attribute), value)
                setattr(unit, model_attribute, float(value))
            #else:
            #    print "SKIPPING: %s" % value

        #agents = { "agent_property_manager":"agent_property_manager", "property_website_url":"property_website_url", "agent_property_manager_address":"agent_property_manager_address", "agent_property_manager_phone":"agent_property_manager_phone", "owner":"owner", }

        agent_name = current["agent_property_manager"].strip()
        agent_site = current["property_website_url"].strip()
        #special case:
        if agent_site == "http://parkermgt.com/":
            pass
        elif re.search('parkermgt', agent_site):
            bldg.website = agent_site
            agent_site = "http://parkermgt.com/"

        agent_address = current["agent_property_manager_address"].strip()
        agent_phone = current["agent_property_manager_phone"].strip()

        owner = current["owner"].strip()

        if agent_name or agent_site or agent_address:
            (person, bldg_person) = make_person(agent_name, bldg, "Agent", address=agent_address, website=agent_site, phone=agent_phone)
            print "created/matched agent: %s" % person.name
            print person

        if owner:
            (owner_person, obldg_person) = make_person(owner, bldg, "Owner")

        #missing:
        #heat_source, renewable_energy

        #other (skip)
        #for listing:
        #"lease_period":"lease_period", "availability":"availability",
        #for utility
        #"electricity_provider":"electricity_provider", "natural_gas_provider":"natural_gas_provider", "utility_info_source":"utility_info_source", "who_pays_for_telephone_land_line":"who_pays_for_telephone_land_line",
        #"comments"
        #energy_saving_features not used consistently, used very similarly to "other_smartliving_features"

        #not sure if this is the right conversion:
        #elif low == 'some exceptions':
        #    clean = True

        bldg.source = feed_source
        bldg.geocoder = "google"

        bldg.save()
        unit.save()
        bldg.update_utility_averages()
        bldg.update_rent_details()

    return address

def read_csv(source_csv, city_tag, feed_date):
    #could also use city.models.find_by_city_state
    city_options = City.objects.filter(tag=city_tag)
    #print "Number of cities available: %s" % len(city_options)
    if not len(city_options):
        raise ValueError, "CITY NOT FOUND! run make_cities.py first"
    else:
        city = city_options[0]

    print city


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


    # ideally, should be able to use the database itself as the cache,
    # instead of using a local file
    # but it's also good to not have to repeat geo queries if going in bulk
    # the site code *will* make geo queries
    # so it's still a good idea to cache the coded address locally
    # even if using the site code for everything else.
    
    cache_file = "%s.json" % city.tag
    #print cache_file
    cache_destination = os.path.join(os.path.dirname(source_csv), cache_file)
    print cache_destination
    #keep a local copy of data we've processed...
    #this should help with subsequent calls
    #to make sure we don't need to duplicate calls to remote geolocation APIs:
    loaded_cache = load_json(cache_destination, create=True)

    #need to go through and load SearchResults separately
    local_cache = {}
    for key in loaded_cache.keys():
        #this is useful if there is a cached value 
        #that was not parsed correctly... this will remove it:
        #if key.strip() == "314 North Washington Street Apt. C":
        if key.strip() == "some address with bad cached data":
            print "not adding: ", key
            #exit()
            pass
        else:
            current = loaded_cache[key]
            results = current['results']
            #print results
            sr = SearchResults()
            #sr.from_dict(results, debug=True)
            sr.from_dict(results, debug=False)
            #print sr
            current['results'] = sr

            #print current['results']
            local_cache[key] = current
        
    #use street address as the key
    #for each address, store SearchResults object

    #reset skips for every run:
    skips = codecs.open("skips.txt", 'w', encoding='utf-8')
    skips.close()


    skips = 0
    #with codecs.open(source_csv, 'rb', encoding='utf-8') as csvfile:
    with open(source_csv) as csvfile:

        #reader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        #reader = csv.reader(csvfile)
        #reader = unicodecsv.UnicodeReader(csvfile, encoding='utf-8')
        reader = unicode_csv_reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())
        print

        keys = []
        for item in reader.next():
            key = item.lower().strip()
            key = key.replace('(', '')
            key = key.replace(')', '')
            key = key.replace('-', '_')
            key = key.replace('.', '')
            key = key.replace('/ ', '')
            key = key.replace('/', '_')
            key = key.replace('"', '')
            key = key.replace('#', 'num')
            key = key.replace(' ', '_')
            keys.append(key)
        
        #*and* the second row in this case
        print '>, <'.join(keys)

        #currently:
        #<street_address>, <unit_if_applicable>, <unit_type>, <rent>, <security_deposit>, <sq_feet_per_unit>, <num_bedrooms>, <num_bathrooms>, <maximum_occupancy_per_unit>, <lease_period>, <availability>, <laundry>, <parking>, <air_conditioning>, <pets>, <gym_fitness_center>, <game_room_rec_center_community_center>, <pool>, <other_amenities>, <bike_friendly>, <recycling>, <composting>, <gardening>, <public_transit>, <walk_friendly>, <other_smartliving_features>, <who_pays_for_electricity>, <who_pays_for_natural_gas>, <who_pays_for_water>, <who_pays_for_trash_recycling_pickup>, <who_pays_for_telephone_land_line>, <who_pays_for_cable>, <who_pays_for_internet>, <electricity_provider>, <electric_utility_cost_average_per_mo>, <electric_utility_cost_low>, <electric_utility_cost_high>, <natural_gas_provider>, <natural_gas_utility_cost_average_per_mo>, <natural_gas_utility_cost_low>, <natural_gas_utility_cost_high>, <energy_saving_features>, <utility_info_source>, <agent_property_manager>, <property_website_url>, <agent_property_manager_address>, <agent_property_manager_phone>, <owner>, <comments>

        #exit()

        count = 0
        #start = 6439
        start = 0

        #if you want to randomize the order... to distribute options more evenly
        #just do this in the original spreadsheet.
        #in order to randomize, should randomize the order in the csv
        for row in reader:

            current = {}
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed (for testing)
            if count > 7220:
                #all_done(cache_destination, local_cache)
                pass

            if count >= start:

                address = process_row(current, row, keys, local_cache, city, feed_source, count)
            
                print

                local_cache[address] = current
                #save every time...
                #never know when a crash will happen:
                #however, this does make things run considerably slower
                #especially once the cached file size grows.
                #save_results(cache_destination, local_cache)

                #exit()
            
    all_done(cache_destination, local_cache)

if __name__ == '__main__':
    feed_date = "2014-11-08"
    city_tag = "bloomington_in"
    #source = '/c/clients/rentrocket/cities/bloomington.csv'
    source = '/c/clients/rentrocket/cities/bloomington/Data_Bloomington_Rental_Master_141010.csv'
    read_csv(source, city_tag, feed_date)
