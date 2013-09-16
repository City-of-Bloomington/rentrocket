import os, json, codecs, re
from helpers import save_json, load_json, Location, Geo, save_results

def update_json(source, city_tag):
    cache_file = "%s.json" % city_tag
    cache_destination = os.path.join(os.path.dirname(source), cache_file)

    local_cache = load_json(cache_destination, create=True)

    assert local_cache.has_key('buildings')
    assert local_cache.has_key('parcels')

    locations = {}
    for key, value in local_cache['buildings'].items():
        location = Location(value)

        for source in location.sources:
            if hasattr(location, source):
                result = getattr(location, source)
                #convert from old dict format here
                if isinstance(result, dict):
                    print "Found dictionary in: %s for: %s" % (source, location.address)

                    result = [ result ]
                    setattr(location, source, result)

        locations[key] = location
        
    #back it up for later
    #enable this when downloading GPS coordinates...
    #the rest of the time it slows things down
    local_cache['buildings'] = {}
    for key, value in locations.items():
        local_cache['buildings'][key] = value.to_dict()
    save_json(cache_destination, local_cache)


if __name__ == '__main__':
    #main()
    #update_json('/c/clients/green_rentals/cities/bloomington/data/Bloomington_rental.csv')
    update_json('/c/clients/green_rentals/cities/ann_arbor/data/ann_arbor.json', "ann_arbor")
