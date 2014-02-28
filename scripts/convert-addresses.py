"""
*2014.02.19 17:20:47
a script to convert the way addresses are stored in the database for many cities.
import scripts did not always keep address as the only item in address field. 

"""
import os, sys, re

sys.path.append(os.path.dirname(os.getcwd()))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

from building.models import Building, Parcel, BuildingPerson, Unit
from city.models import City
from rentrocket.helpers import to_tag

#city_options = City.objects.filter(tag="columbia_mo")
city_options = City.objects.filter(tag="bloomington_in")
print "Number of cities available: %s" % len(city_options)
if not len(city_options):
    raise ValueError, "CITY NOT FOUND! run make_cities.py first"
else:
    city = city_options[0]

buildings = Building.objects.filter(city=city)
print len(buildings)
print buildings.count()
mismatched = 0
count = 0
#for building in buildings[:10]:
for building in buildings:
    if re.search("USA", building.address) or re.search("United States", building.address):
        print 
        print "Starting %04d: %s" % (count, building.address)
        #this is one that needs conversion
        parts = building.address.split(',')
        if re.search(', Indiana University Bloomington, ', building.address):
            [street, street2, city_part, state_zip, country] = parts
        elif re.search(', Staples, ', building.address):
            [street, street2, city_part, state_zip, country] = parts
        elif re.search(', Dunnkirk Square, ', building.address):
            [street, street2, city_part, state_zip, country] = parts
        else:
            [street, city_part, state_zip, country] = parts

        print street
        if re.search('#', street):
            #matched a unit in the address
            #take care of splitting and merging these
            street, unit = street.split('#')
            unit = '#' + unit
            print unit

            #check if we have an existing building we can merge this one into
            matches = Building.objects.filter(city=city).filter(address=street)
            if len(matches):
                building_match = matches[0]
                print "Found existing building with address: ", street
                #already have one with base address
                #check units
                #if there is a blank unit, use that
                #create new units if no others match
                blank_unit = False
                blank_count = 0
                matched_unit = None
                #if building_match.units.count():
                for bmunit in building_match.units.all():
                    if not bmunit.number:
                        blank_unit = bmunit
                        blank_count += 1
                    #could select/filter for this, but since we want blanks too
                    #loop is fine
                    elif bmunit.number == unit:
                        matched_unit = bmunit

                if not matched_unit:
                    #if we didn't have a matching unit already,
                    #use either an existing blank unit
                    if blank_unit:
                        if blank_count > 1:
                            raise ValueError, "More than one blank unit found. This shouldn't happen"
                        else:
                            blank_unit.number = unit
                            blank_unit.save()
                    #or create a new one
                    else:
                        nunit = Unit()
                        nunit.building = building_match
                        nunit.number = unit
                        nunit.address = building_match.address + ", " + unit
                        nunit.save()

                #at this point assume we've created a corresponding unit on
                #the building_match object...
                #delete the original:
                building.delete()
                building = building_match
            else:
                #convert this building to be a main building with a single unit
                print "Converting building from: %s to %s" % (building.address, street)
                building.address = street

                matched = False
                #assert building.units.count() == 0
                if building.units.count():
                    for bu in building.units.all():
                        if bu.number == unit:
                            print "ALREADY HAD UNIT!: %s" % unit
                            matched = True
                        print bu.number
                    #exit()

                if not matched:
                    nunit = Unit()
                    nunit.building = building
                    nunit.number = unit
                    nunit.address = building.address + ", " + unit
                    nunit.save()

        else:
            #didn't match a unit number... just update the address
            building.address = street
            

        city_part = city_part.strip()
        print city_part
        if to_tag(city_part) != to_tag(city.name):
            print "WARNING: city does not match: %s != %s" % (city.name, city_part)
            print to_tag(city_part), str(city.tag)
            mismatched += 1

        print state_zip
        state_zip = state_zip.strip()
        parts = state_zip.split(' ')
        if len(parts) == 2:
            state, postal_code = parts
        elif len(parts) == 1:
            state = parts[0]
            postal_code = ''
        else:
            state = ''
            postal_code = ''
            
        print state
        print postal_code
        building.postal_code = postal_code

        #this should call save:
        building.create_tag(force=True)
        building.save()
        
        #print parts
        #print building.state
        #print building.city.name

    else:
        #didn't match "USA" in address... must be OK

        #can repeat any necessary tasks here, if needed:
        ## print "updating tag for: %s" % building.address
        ## building.create_tag(force=True)
        ## building.save()
        
        pass
        
    count += 1
        
print "Total number of addresses that do not match city: ", mismatched
