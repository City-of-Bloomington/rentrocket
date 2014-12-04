from django.db import models
from rentrocket.helpers import to_tag

from rentrocket.helpers import get_client_ip, address_search, check_result

#rather than do a lookup for some of these items
#just reference a local cache...
#not that many.
#
#still need to have in the database for ForeignKey purposes
#
#to update
#cd scripts 
#python make_cities.py
#then copy in from cities.json
#
# should only include officially supported cities here...
# will be adding other cities in as City objects
all_cities = {"albany_ny": {"lat": 42.6525793, "state": "NY", "tag": "albany_ny", "name": "Albany", "lng": -73.7562317}, "fayetteville_ar": {"lat": 36.0625795, "state": "AR", "tag": "fayetteville_ar", "name": "Fayetteville", "lng": -94.1574263}, "austin_tx": {"lat": 30.267153, "state": "TX", "tag": "austin_tx", "name": "Austin", "lng": -97.7430608}, "madison_wi": {"lat": 43.0730517, "state": "WI", "tag": "madison_wi", "name": "Madison", "lng": -89.4012302}, "oklahoma_city_ok": {"lat": 35.4675602, "state": "OK", "tag": "oklahoma_city_ok", "name": "Oklahoma City", "lng": -97.5164276}, "berkeley_ca": {"lat": 37.8715926, "state": "CA", "tag": "berkeley_ca", "name": "Berkeley", "lng": -122.272747}, "evanston_il": {"lat": 42.0450722, "state": "IL", "tag": "evanston_il", "name": "Evanston", "lng": -87.68769689999999}, "lawrence_ks": {"lat": 38.9716689, "state": "KS", "tag": "lawrence_ks", "name": "Lawrence", "lng": -95.2352501}, "columbia_mo": {"lat": 38.9517053, "state": "MO", "tag": "columbia_mo", "name": "Columbia", "lng": -92.3340724}, "burlington_vt": {"lat": 44.4758825, "state": "VT", "tag": "burlington_vt", "name": "Burlington", "lng": -73.21207199999999}, "bloomington_in": {"lat": 39.165325, "state": "IN", "tag": "bloomington_in", "name": "Bloomington", "lng": -86.52638569999999}, "dearborn_mi": {"lat": 42.3222599, "state": "MI", "tag": "dearborn_mi", "name": "Dearborn", "lng": -83.17631449999999}, "ann_arbor_mi": {"lat": 42.2808256, "state": "MI", "tag": "ann_arbor_mi", "name": "Ann Arbor", "lng": -83.7430378}, "iowa_city_ia": {"lat": 41.6611277, "state": "IA", "tag": "iowa_city_ia", "name": "Iowa City", "lng": -91.5301683}}

def make_city(result):
    """
    assume we've already checked for existing here...
    part of that check should have involved a call to address_search...
    no need to duplicate that here...
    we just need to process the result
    """

    error = None
    city = None
    
    city_tag = to_tag("%s_%s" % (result['city'], result['state']))

    city = City()
    city.name = result['city']
    city.tag = city_tag
    city.state = result['state']

    city.latitude = result['lat']
    city.longitude = result['lng']

    city.save()

    return (city, error)

def find_by_city_state(city_name, city_state):
    """
    check for existing...
    """
    city = None
    city_tag = to_tag("%s_%s" % (city_name, city_state))
    city_options = City.objects.filter(tag=city_tag)
    
    #print "Number of cities available: %s" % len(city_options)
    #if not len(city_options):
    #    (city, error) = search_city("%s, %s" % (city_name, city_state), make)
    if len(city_options):    
        city = city_options[0]
    return city

def lookup_city_with_geo(search_results, make=False):
    """
    geo_lookup should have already happened... pass those in
    """
    error = None
    if len(search_results.matches) == 1:
        #print search_results.matches
        result = search_results.matches[0]

        #probably ok to skip this here... it should have been done earlier..
        #could also get rid of one level of conditionals in that case:
        #error = check_result(result)
        #if not error:

        city = find_by_city_state(result['city'], result['state'])
        if not city and make:
            (city, error) = make_city(result)

        if city:
            search_results.city = city
        if error:
            search_results.errors.append(error)

        #else:
        #    search_results.errors.append(error)
                
    elif len(search_results.matches) > 1:
        error = "More than one (%s) city found %s" % (len(search_results.matches), search_results.matches)
        search_results.errors.append(error)

        #city = None

    elif len(search_results.matches) < 1: 
        #print "WARNING! no match found: ", search_results.matches
        error = "No city found"
        search_results.errors.append(error)
        #city = None

    #return (city, error)

def search_city(query, make=False):
    """
    in this version, we'll do the geo query to normalize the search
    then see if we have a matching city

    if not, and if make is True, then we can call make_city
    """
    results = address_search(query)
    #(results, error, unit) = address_search(query)
    #results = address_search(query)
    #(city, error) = lookup_city_with_geo(results, make)
    lookup_city_with_geo(results, make)
    #return (city, error, results)    
    return results


# really need both city_name and state_name...
# if you only have one, it's going to cause problems
# too many chances for ambiguity!
## def search_city_local(city_name):
##     """
##     check for existing...
##     useful if no state data is available
##     but may return more than one
##     but also avoids a geo lookup request (address_search())
##     """
##     city_options = City.objects.filter(name=city_name)
    
##     #print "Number of cities available: %s" % len(city_options)
##     #if not len(city_options):
##     #    (city, error) = search_city("%s, %s" % (city_name, city_state), make)
##     #if len(city_options):    
##     #    city = city_options[0]
##     return city_options


## def find_by_city_state(city_name, city_state, make=False):
##     """
##     want to call this as part of other searches...
##     don't want to include make here
    
##     first check for existing...
##     if not found, create new.
##     """

##     error = None
##     city_tag = to_tag("%s_%s" % (city_name, city_state))
##     city_options = City.objects.filter(tag=city_tag)
    
##     #print "Number of cities available: %s" % len(city_options)
##     if not len(city_options):
##         (city, error) = search_city("%s, %s" % (city_name, city_state), make)
##     else:
##         city = city_options[0]
##     return (city, error)    

## original version that did not use SearchResults object
## def lookup_city_with_geo(search_options, make=False):
##     """
##     geo_lookup should have already happened... pass those in
##     """
##     error = None
##     if len(search_options) == 1:
##         #print search_options
##         result = search_options[0]
##         error = check_result(result)
##         if not error:
##             city = find_by_city_state(result['city'], result['state'])
##             if not city and make:
##                 (city, error) = make_city(result)
##             else:
##                 city = None
                
##     elif len(search_options) > 1:
##         #print "WARNING! more than one match found: ", search_options
##         error = "WARNING! more than one (%s) city found %s" % (len(search_options), search_options)
##         city = None

##     elif len(search_options) < 1: 
##         #print "WARNING! no match found: ", search_options
##         error = "WARNING! no match found"
##         city = None

##     return (city, error)
    
class City(models.Model):
    """
    Details to define a specific City
    """
    #Name of the municipality providing this feed.
    #For example 'San Francisco' or 'Multnomah County'
    #municipality_name = models.CharField(max_length=20)

    name = models.CharField(max_length=200)

    #URL of the publishing municipality's website
    url = models.CharField(max_length=100, blank=True)

    #this is what we'll use to look up a city:
    tag = models.CharField(max_length=200, unique=True, default=to_tag(str(name)))

    #in case we want to represent other types of municipalities, not just cities
    type = models.CharField(max_length=50, default="city")

    #State where the property is located.
    #In the U.S. this should be the two-letter code for the state
    state = models.CharField(max_length=2)

    #where to center the map when choosing this location
    latitude = models.FloatField()
    longitude = models.FloatField()

    #these are the values used to assign a marker
    #based on where a building's energy score falls in these.
    #these are set while running "generate_city_stats.py" script
    cutoffs = models.CharField(max_length=200, default="50,250,500,1000")

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    def name_tag(self):
        """
        sometimes we only need the city name as a tag
        (e.g. energy data uploads)
        vs the standard tag of cityname_state
        """
        return to_tag(str(self.name))
