import os, json, codecs, re

from geopy import geocoders, distance

def save_results(locations, destination="test.tsv"):
    #destination = "test.tsv"
    print "Saving: %s results to %s" % (len(locations), destination)
    with codecs.open(destination, 'w', encoding='utf-8') as out:
        #print locations.values()[0].make_header()
        out.write(locations.values()[0].make_header())
        for key, location in locations.items():
            location.compare_points()
            #print location.make_row()
            out.write(location.make_row())
    exit()
    
class Location(object):
    """
    hold geolocation data associated with a specific address

    making an object to help with processing results consistently
    """
    def __init__(self, dictionary={}):
        """
        http://stackoverflow.com/questions/1305532/convert-python-dict-to-object
        """
        self.__dict__.update(dictionary)

        self.sources = ["google", "bing", "usgeo", "geonames", "openmq", "mq"]

    def to_dict(self):
        """
        http://stackoverflow.com/questions/61517/python-dictionary-from-an-objects-fields
        """
        result = self.__dict__.copy()
        #can't remove('sources') on a dict
        result.pop('sources', None)
        return result

    def compare_points(self):

        #find only points with something in them
        options = {}
        for source in self.sources:
            if hasattr(self, source) and getattr(self, source)['place']:
                options[source] = getattr(self, source)

        d = distance.distance

        available = options.keys()

        self.distances = {}
        self.totals = {}
        index = 1
        for item in available:
            total = 0
            others = available[:]
            if item in others:
                others.remove(item)
            for other in others:
                pt1 = ( options[item]['lat'], options[item]['lng'] )
                pt2 = ( options[other]['lat'], options[other]['lng'] )
                key = "%s-%s" % (item, other)

                #https://github.com/geopy/geopy/blob/master/geopy/distance.py
                #miles are also an option
                #cur_d = d(pt1, pt2).miles
                cur_d = d(pt1, pt2).feet
                if not self.distances.has_key(key):
                    self.distances[key] = cur_d
                total += cur_d
            #this will be the same for all items if adding everything
            self.totals[item] = total

    def min_max_distances(self):
        if not self.distances:
            self.compare_points()

        sortable = []
        for key, value in self.distances.items():
            sortable.append( (value, key) )

        sortable.sort()
        
        if len(sortable) >= 2:
            return ( sortable[0], sortable[-1] )
        else:
            return ( ('', ''), ('', '') )
    

    def min_max_totals(self):
        if not self.distances:
            self.compare_points()

        sortable = []
        for key, value in self.totals.items():
            sortable.append( (value, key) )

        sortable.sort()
        if len(sortable) >= 2:
            return ( sortable[0], sortable[-1] )
        else:
            return ( ('', ''), ('', '') )
    
    def make_header(self):
        """
        return a row representation of the header (for CSV output)
        """
        header = [ 'search', 'address', '' ]
        header.extend( self.sources )
        header.extend( [ '', 'closest', 'closest_amt', 'furthest', 'furthest_amt', '' ] )
        header.extend( [ '', 'tclosest', 'tclosest_amt', 'tfurthest', 'tfurthest_amt', '' ] )

        index = 1
        for item1 in self.sources:
            for item2 in self.sources[index:]:
                title = "%s-%s" % (item1, item2)
                header.append(title)

        return "\t".join(header)  + '\n'

    def make_row(self):
        """
        return a row representation of our data (for CSV output)
        """

        ## for source in self.sources:
        ##     if self.get
        ##     if source == 'google':
        ##         #set this as the default
        ##         if location.google['place']:
        ##             location.address = location.google['place']
        ##         else:
        ##             #TODO
        ##             #maybe check other places?
        ##             location.address = ''


        #row = [ self.address ]

        row = []
        found_address = False
        for source in self.sources:
            if hasattr(self, source) and getattr(self, source)['place']:
                cur = getattr(self, source)
                ll = "%s, %s" % (cur['lat'], cur['lng'])
                #pick out the first address that has a value
                if not found_address:
                    self.address = cur['place']
                    row.insert(0, '')
                    row.insert(0, self.address)
                    row.insert(0, self.address_alt)
                    found_address = True
            else:
                ll = ''
            row.append( ll )

        #couldn't find an address anywhere:
        if not found_address:
            row.insert(0, '')
            row.insert(0, '')
            row.insert(0, self.address_alt)
            print "ERROR LOCATING: %s" % self.address_alt

        (mi, ma) = self.min_max_distances()
        # 'closest', 'closest_amt', 'furthest', 'furthest_amt', 
        row.extend( [ '', mi[1], str(mi[0]), ma[1], str(ma[0]), '' ] )

        (mi, ma) = self.min_max_totals()
        # 'closest', 'closest_amt', 'furthest', 'furthest_amt', 
        row.extend( [ '', mi[1], str(mi[0]), ma[1], str(ma[0]), '' ] )

        index = 1
        for item1 in self.sources:
            for item2 in self.sources[index:]:
                title = "%s-%s" % (item1, item2)
                if self.distances.has_key(title):
                    row.append(str(self.distances[title]))
                else:
                    row.append('')
                    
        return "\t".join(row) + '\n'

        
class Geo(object):
    """
    object to assist with geocoding tasks...
    wraps geopy
    and initializes coders in one spot
    """

    def __init__(self):

        #initialize geocoders once:
        self.google = geocoders.GoogleV3()
        #doesn't look like yahoo supports free api any longer:
        #http://developer.yahoo.com/forum/General-Discussion-at-YDN/Yahoo-GeoCode-404-Not-Found/1362061375511-7faa66ba-191d-4593-ba63-0bb8f5d43c06
        #yahoo = geocoders.Yahoo('PCqXY9bV34G8P7jzm_9JeuOfIviv37mvfyTvA62Ro_pBrwDtoIaiNLT_bqRVtETpb79.avb0LFV4U1fvgyz0bQlX_GoBA0s-')
        self.usgeo = geocoders.GeocoderDotUS() 
        self.geonames = geocoders.GeoNames()
        self.bing = geocoders.Bing('AnFGlcOgRppf5ZSLF8wxXXN2_E29P-W9CMssWafE1RC9K9eXhcAL7nqzTmjwzMQD')
        self.openmq = geocoders.OpenMapQuest()
        self.mq = geocoders.MapQuest()

        #skipping mediawiki, seems less complete?
        #mediawiki = geocoders.MediaWiki("http://wiki.case.edu/%s")


    def lookup(self, address, source="google", location=None):
        """
        look up the specified address using the designated source
        if location dictionary is specified (for local caching)
        store results there

        return results either way
        """

        if not location is None:
            self.location = location
        else:
            self.location = Location()

        if not hasattr(location, source):
            print "Looking for: %s in %s" % (address, source)
            try:
                coder = getattr(self, source)
                place, (lat, lng) = coder.geocode(address)  
                print "Result was: %s" % place
                print "lat: %s, long: %s" % (lat, lng)
                setattr(location, source, {'place': place, 'lat': lat, 'lng': lng})
                #local_cache_cur[source] = {'place': place, 'lat': lat, 'lng': lng} 
            except:
                setattr(location, source, {'place': None, 'lat': None, 'lng': None})
                #local_cache_cur[source] = {'place': None, 'lat': None, 'lng': None}

        else:
            print "Already have %s results for: %s" % (source, address)



        ## if not local_cache_cur.has_key('google'):
        ##     print "Looking for: %s in Google" % search
        ##     place, (lat, lng) = google.geocode(search)  

        ##     print "Result was: %s" % place
        ##     print "lat: %s, long: %s" % (lat, lng)
        ##     local_cache_cur['google'] = {'place': place, 'lat': lat, 'lng': lng}
        ## else:
        ##     print "Already have google results for: %s" % address

        ## ## if not local_cache_cur.has_key('yahoo'):
        ## ##     print "Looking for: %s in Yahoo" % search
        ## ##     place, (lat, lng) = yahoo.geocode(search)  
        ## ##     print "Result was: %s" % place
        ## ##     print "lat: %s, long: %s" % (lat, lng)
        ## ##     local_cache_cur['yahoo'] = {'place': place, 'lat': lat, 'lng': lng}
        ## ## else:
        ## ##     print "Already have yahoo results for: %s" % address

        ## #usgeo = geocoders.GeocoderDotUS() 
        ## #geonames = geocoders.GeoNames()
        ## #bing = geocoders.Bing()
        ## #openmq = geocoders.OpenMapQuest()
        ## #mq = geocoders.MapQuest()

        ## if not local_cache_cur.has_key('usgeo'):
        ##     print "Looking for: %s in Usgeo" % search
        ##     try:
        ##         place, (lat, lng) = usgeo.geocode(search)  
        ##         print "Result was: %s" % place
        ##         print "lat: %s, long: %s" % (lat, lng)
        ##         local_cache_cur['usgeo'] = {'place': place, 'lat': lat, 'lng': lng}
        ##     except:
        ##         local_cache_cur['usgeo'] = {'place': None, 'lat': None, 'lng': None}

        ## else:
        ##     print "Already have usgeo results for: %s" % address

        ## if not local_cache_cur.has_key('geonames'):
        ##     print "Looking for: %s in Geonames" % search
        ##     try:
        ##         place, (lat, lng) = geonames.geocode(search)  
        ##         print "Result was: %s" % place
        ##         print "lat: %s, long: %s" % (lat, lng)
        ##         local_cache_cur['geonames'] = {'place': place, 'lat': lat, 'lng': lng}
        ##     except:
        ##         local_cache_cur['geonames'] = {'place': None, 'lat': None, 'lng': None}

        ## else:
        ##     print "Already have geonames results for: %s" % address

        ## if not local_cache_cur.has_key('bing'):
        ##     print "Looking for: %s in Bing" % search
        ##     place, (lat, lng) = bing.geocode(search)  
        ##     print "Result was: %s" % place
        ##     print "lat: %s, long: %s" % (lat, lng)
        ##     local_cache_cur['bing'] = {'place': place, 'lat': lat, 'lng': lng}
        ## else:
        ##     print "Already have bing results for: %s" % address

        ## if not local_cache_cur.has_key('openmq'):
        ##     print "Looking for: %s in Openmq" % search
        ##     place, (lat, lng) = openmq.geocode(search)  
        ##     print "Result was: %s" % place
        ##     print "lat: %s, long: %s" % (lat, lng)
        ##     local_cache_cur['openmq'] = {'place': place, 'lat': lat, 'lng': lng}
        ## else:
        ##     print "Already have openmq results for: %s" % address

        ## #got multiple results here
        ## #could re-enable if others start getting multiple results
        ## ## if not local_cache_cur.has_key('mq'):
        ## ##     print "Looking for: %s in Mq" % search
        ## ##     place, (lat, lng) = mq.geocode(search)  
        ## ##     print "Result was: %s" % place
        ## ##     print "lat: %s, long: %s" % (lat, lng)
        ## ##     local_cache_cur['mq'] = {'place': place, 'lat': lat, 'lng': lng}
        ## ## else:
        ## ##     print "Already have mq results for: %s" % address


    

def save_json(destination, json_objects):
    json_file = codecs.open(destination, 'w', encoding='utf-8', errors='ignore')
    json_file.write(json.dumps(json_objects))
    json_file.close()    

def load_json(source_file, create=False):
    if not os.path.exists(source_file):
        json_objects = {}
        if create:
            print "CREATING NEW JSON FILE: %s" % source_file
            json_file = codecs.open(source_file, 'w', encoding='utf-8', errors='ignore')
            #make sure there is something there for subsequent loads
            json_file.write(json.dumps(json_objects))
            json_file.close()
        else:
            raise ValueError, "JSON file does not exist: %s" % source_file
    else:
        json_file = codecs.open(source_file, 'r', encoding='utf-8', errors='ignore')

        try:
            json_objects = json.loads(json_file.read())
        except:
            raise ValueError, "No JSON object could be decoded from: %s" % source_file
        json_file.close()
    return json_objects

