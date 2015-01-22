import sys, os

sys.path.append(os.path.dirname(os.getcwd()))

#http://stackoverflow.com/questions/8047204/django-script-to-access-model-objects-without-using-manage-py-shell
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rentrocket.settings")

## from rentrocket import settings
## from django.core.management import setup_environ
## setup_environ(settings)

import csv

from city.models import City, search_city, find_by_city_state
from utility.models import ServiceProvider, ServiceUtility, CityServiceProvider
from building.models import UTILITY_TYPES

def unicode_csv_reader(utf8_data, dialect=csv.excel, **kwargs):
    csv_reader = csv.reader(utf8_data, dialect=dialect, **kwargs)
    for row in csv_reader:
        yield [unicode(cell, 'utf-8') for cell in row]


def read_csv(source_csv):

    count = 0
    #with codecs.open(source_csv, 'rb', encoding='utf-8') as csvfile:
    with open(source_csv) as csvfile:
        reader = unicode_csv_reader(csvfile)

        #just print the first row:
        print '>, <'.join(reader.next())

        for row in reader:
            count += 1
            print "Looking at row: %s" % count
            
            #could exit out early here, if needed
            if count > 10:
                #exit()
                pass

            city_name = row[0]
            state_name = row[1]
            utility_type = row[2]
            provider_name = row[3]
            provider_site = row[4]
            provider_phone = row[5]
            
            #print city_name
            #city_options = search_city_local(city_name)
            city = find_by_city_state(city_name, state_name)
            if not city:
                query = "%s, %s" % (city_name, state_name)
                results = search_city(query, make=True)
                print results
                print dir(results)
                if results.errors or not results.city:
                    print results.errors
                    
                    raise ValueError, "Problem creating city: %s" % (city_name)
                else:
                    city = results.city
                
            ## if len(city_options) > 1:
            ##     #could try doing a geo search, but that seems prone to error too
            ##     #really need more information here
            ##     raise ValueError, "More than one matching city found: %s" % (city_name)
            ## elif len(city_options) == 0:
                    
            ## else:
            ##     city = city_options[0]

             
            #print city_options
            print city.name
            print city.state

            provider_options = ServiceProvider.objects.filter(name=provider_name)
            if len(provider_options):
                provider = provider_options[0]
            elif provider_name:
                #make a new one:
                provider = ServiceProvider()
                provider.name = provider_name
            else:
                provider = None

            if provider:
                if provider.website != provider_site:
                    print "UPDATING SITE: ",
                    print provider.website
                    print len(provider_site)
                    provider.website = provider_site

                if provider.phone != provider_phone:
                    print "UPDATING PHONE: ",
                    print provider.phone
                    print provider_phone
                    provider.phone = provider_phone

                provider.save()
            

                matched = False
                match = None
                for ut in UTILITY_TYPES:
                    if ut[1] == utility_type:
                        match = ut

                print utility_type
                print match

                if match:
                    utility_options = ServiceUtility.objects.filter(provider=provider, type=match[0])
                    if len(utility_options):
                        print "matched existing ServiceUtility: %s" % len(utility_options)
                        sutility = utility_options[0]
                    else:
                        print "Creating new ServiceUtility"
                        #make a new one:
                        sutility = ServiceUtility()
                        sutility.type = match[0]
                        sutility.provider = provider
                        sutility.save()


                city_options = CityServiceProvider.objects.filter(provider=provider, city=city)
                if len(city_options):
                    city_service = city_options[0]
                else:
                    #make a new one:
                    city_service = CityServiceProvider()
                    city_service.city = city
                    city_service.provider = provider
                    city_service.save()
                
            ## print "Number of cities available: %s" % len(city_options)
            print provider_name
            print provider_site
            print provider_phone

            print            

if __name__ == '__main__':
    read_csv('/c/clients/rentrocket/cities/service_providers.csv')
