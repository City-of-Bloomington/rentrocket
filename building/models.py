import re, json, copy

from django.db import models

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

from jsonfield import JSONField

from source.models import Source
from city.models import City, lookup_city_with_geo, find_by_city_state
from person.models import Person
from rentrocket.helpers import to_tag, MultiSelectField, check_result, address_search, get_client_ip

from urllib import urlencode

#originally in utility/models.py
#but they are needed here and this gets imported first
UTILITY_TYPES = (
    ('electricity', 'Electricity'),
    ('gas', 'Natural Gas'),
    ('oil', 'Heating Oil'),    
    ('water', 'Water'),
    ('sewage', 'Sewage'),
    ('trash', 'Trash'),
    ('recycling', 'Recycling'),

    ('other', 'Other'),

    ## ('storm', 'Storm Water'),
    ## ('compo', 'Compost'),
    ## ('data', 'Data'),
    ## ('video', 'Video'),
    ## ('phone', 'Phone'),
    ## ('dv', 'Data+Video'),
    ## ('video', 'Video+Phone'),
    ## ('dp', 'Data+Phone'),
    ## ('dvp', 'Data+Video+Phone'),
    ## ('wifi', 'Wifi'),

    )



#http://stackoverflow.com/questions/1355150/django-when-saving-how-can-you-check-if-a-field-has-changed
class ModelDiffMixin(object):
    """
    A model mixin that tracks model fields' values and provide some useful api
    to know what fields have been changed.
    """

    def __init__(self, *args, **kwargs):
        super(ModelDiffMixin, self).__init__(*args, **kwargs)
        self.__initial = self._dict

    @property
    def diff(self):
        d1 = self.__initial
        d2 = self._dict
        diffs = [(k, (v, d2[k])) for k, v in d1.items() if v != d2[k]]
        return dict(diffs)

    @property
    def has_changed(self):
        return bool(self.diff)

    @property
    def changed_fields(self):
        return self.diff.keys()

    def get_field_diff(self, field_name):
        """
        Returns a diff for field if it's changed and None otherwise.
        """
        return self.diff.get(field_name, None)

    def save(self, *args, **kwargs):
        """
        Saves model and set initial state.
        """
        super(ModelDiffMixin, self).save(*args, **kwargs)
        self.__initial = self._dict

    @property
    def _dict(self):
        return model_to_dict(self, fields=[field.name for field in
                             self._meta.fields])

class Parcel(models.Model):
    """
    AKA Property, but 'property' is a built in function of Python,
    so avoiding confusion by naming it Parcel instead.
    """
    ## parcel_id
    ## string
    ## Yes
    ## Local identifier for all parcel footprint that the building sits on.
    #django should provide this by default
    #if a city provides it, we will need to override the default
    #id = models.CharField(max_length=10, primary_key=True)

    #buildings have addresses, but not parcels:
    #address = models.CharField(max_length=200)

    #supplied by source
    custom_id = models.CharField(max_length=50, unique=True)

    ## Shape
    ## geometry
    ## Yes
    ## This field contains data that describes the boundaries of the lot. It is generated automatically when the shapefile is created and will display a type of polygon or multipolygon.
    shape = models.TextField()

    #Lowest numerical value of the street number
    #if the building has an address range or only building street number.
    from_st = models.CharField(max_length=12)

    #Highest numerical value of the street number
    #if the building has an address range.
    to_st = models.CharField(max_length=12, blank=True)

    street = models.CharField(max_length=50)

    street_type = models.CharField(max_length=10)

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    #isn't it possible that more than one building could be on a parcel,
    #but only one parcel for any given building?
    #if so, following is *not* needed here (link happens from the building)
    #
    #if not (if building could span multiple parcels),
    #then we need a different relation between the two
    ## building_id
    ## string
    ## Yes
    ## Unique identifier for the residential building.  Can correspond to more than one parcel_id or an address range


def make_unit(apt_num, building):
    unit = None

    #check for existing:
    #should have already checked using building.find_unit()
    #could disable check if that is working
    units = Unit.objects.filter(building=building).filter(number=apt_num)

    #check if a previous unit object in the db exists
    if units.exists():
        unit = units[0]
        #print "Already had Unit: %s" % unit.address
    else:
        #now check if we have a blank unit with the building...
        #might have added just the building before we knew about unit specifics
        #
        #all buildings need at least one unit, so we may have a blank one
        #use that first if so...
        blank_count = 0
        blank_unit = False

        #this is similar to building.find_unit
        #but looks for blanks too
        for bldg_unit in building.units.all():
            if not bldg_unit.number:
                blank_unit = bldg_unit
                blank_count += 1

            ## # shouldn't ever reach this case with initial filter
            ## #
            ## #could select/filter for this, but since we want blanks too
            ## #loop is fine
            ## elif bldg_unit.number == apt_num:
            ##     unit = bldg_unit

        if not unit:
            #if we didn't have a matching unit already,
            #use either an existing blank unit
            if blank_unit:
                if blank_count > 1:
                    raise ValueError, "More than one blank unit found. This shouldn't happen"
                else:
                    blank_unit.number = apt_num
                    blank_unit.save()
                    blank_unit.create_tag(force=True)
                    unit = blank_unit

            #or create a new one
            else:
                unit = Unit()
                unit.building = building
                unit.number = apt_num
                #DON'T DO THIS! (see Unit.__init__)
                # don't want to set this unless it's different:
                #unit.address = building.address + ", " + unit
                unit.save()    
                unit.create_tag(force=True)

    return unit


def make_building(search_results, bldg_id=None, parcel_id=None, source=None, request=None):
    """
    assume we've already checked for existing here...
    part of that check should have involved a call to address_search...
    no need to duplicate that here...
    we just need to process the result
    """

    #(city, error) = lookup_city_with_geo(search_results, make=True)
    lookup_city_with_geo(search_results, make=True)
    city = search_results.city

    #should have already checked that there is only one!
    result = search_results.matches[0]

    if not result.has_key('street') or not city:
        search_results.errors.append("Cannot add a new building without a street address and a city.")
    else:

        if parcel_id:
            cid = parcel_id
        elif bldg_id:
            cid = "%s-%s" % (city.tag, bldg_id)
        else:
            cid = ''

        parcel = None
        #if cid == '', we'll get one empty parcel for every building
        #but that is probably ok...
        #should only add a parcel if we know something about it
        #(even if that is just the ID a city uses for it)
        #if cid:

        #print "Checking parcel id: %s" % (cid)
        parcels = Parcel.objects.filter(custom_id=cid)
        if parcels.exists():
            parcel = parcels[0]
            #print "Already had parcel: %s" % parcel.custom_id


        # if we don't have one, just make a new one
        if not parcel:
            parcel = Parcel()
            parcel.custom_id = cid
            parcel.save()
            #print "Created new parcel: %s" % parcel.custom_id

        bldg = Building()

        bldg.address = result['street']
        bldg.latitude = float(result['lat'])
        bldg.longitude = float(result['lng'])

        bldg.parcel = parcel
        bldg.geocoder = "Google"
        if source:
            #not going to try to create one of these otherwise
            bldg.source = source

        ## elif request:
        ##     bldg.source = "Web:%s" % get_client_ip(request)
        ## else:
        ##     #delete this after request passing attempted
        ##     #raise ValueError, "Have you tried passing in request yet?"
        ##     bldg.source = "Web"

        bldg.city = city
        bldg.state = city.state

        bldg.postal_code = result['zipcode']

        #print updated.diff
        changes = ChangeDetails()

        if request:
            changes.ip_address = get_client_ip(request)
            if request.user:
                changes.user = request.user
        else:
            #set a default to show that this change was made from a script
            changes.ip_address = "1.1.1.1"

        changes.diffs = json.dumps(bldg.diff)
        #not required
        #changes.unit =
        #print changes.diffs

        bldg.save()

        #waiting to make sure bldg has an id:
        changes.building = bldg
        changes.save()

        bldg.create_tag(force=True)

        #delaying creating an associated Unit here...
        #may have multiple units that we want to add
        #every building should have at least one Unit associated with it though

        search_results.building = bldg
        search_results.created = True
        #return (bldg, error)

def find_building(result):
    """
    check for existing...
    take the whole checked result here

    not worried about making here...
    so if we don't have a city, we don't have a building, just return None
    """

    building = None
    error = None
    
    city = find_by_city_state(result['city'], result['state'])
            
    if city and result.has_key('street'):
        #at this point we should have done the normalization... want the equal
        #bq = Building.objects.all().filter(city=city).filter(address__icontains=result['street']).order_by('-energy_score')
        bq = Building.objects.all().filter(city=city).filter(address=result['street']).order_by('-energy_score')

        if len(bq) > 1:
            error = "More than one building found. Please be more specific: %s" % len(bq)
        elif len(bq) == 1:
            building = bq[0]
        else:
            #error = "No building matched"
            pass

    else:
        #if we don't have a city, we certainly won't have a building
        building = None

    return [building, error]

def lookup_building_with_geo(search_results, make=False, request=None, parcel_id=None):
    """
    address_search should have already happened... pass those results in

    then see if we have a matching building

    if not, and if make is True, then we can call make_building
    """
    error = None
    #unit = None
    if len(search_results.matches) == 1:
        #print search_results.matches
        result = search_results.matches[0]

        #same as city... this check should have happened already
        #error = check_result(result)
        #if not error:

        #down to one result... add unit_search in to that
        #this should be set already now:
        #result['unit'] = unit_search

        (building, error) = find_building(result)
        if error:
            search_results.errors.append(error)

        #print "Building: ", building
        #print "Error: ", error
        if not building and not error and make:
            #(building, error) = make_building(result, request=request)
            make_building(search_results, request=request, parcel_id=parcel_id)
            building = search_results.building
            
        if building:
            search_results.building = building

            #regardless of if we have a value for unit_search
            # (aka search_results.unit_text)
            #want to look up the unit (blank ones included)

            (match, error, matches) = building.find_unit(search_results.unit_text)
            #print "Find Unit Results: ->%s<- ->%s<- ->%s<-" % (match, error, matches)
            
            if match:
                #unit = match
                search_results.unit = match
            elif not match and not error and make:
                print "BUILDING UNITS: %s, (%s)" % (building.units, building.units.count())
                if not search_results.unit_text and building.units.count():
                    #*but* if the unit_search is blank
                    #and the building already has units,
                    #we don't want to create another blank one
                    print "Already have units. Not making a blank one!"
                    search_results.unit = None
                else:
                    #if search_results.unit_text is '',
                    #this should create a blank unit:
                    unit = make_unit(search_results.unit_text, building)
                    #print "Made new unit: ", unit
                    search_results.unit = unit
                    search_results.created = True
                
            if error:
                search_results.errors.append(error)

    elif len(search_results.matches) > 1:
        error = "More than one match found. Please narrow your selection."
        search_results.errors.append(error)
        #building = None

    elif len(search_results.matches) < 1: 
        error = "No match found. Please check the address."
        search_results.errors.append(error)
        #building = None
    
def search_building(query, unit='', make=False, request=None):
    """
    in this version, we'll do the geo query to normalize the search
    then pass it on to lookup_building_with_geo...
    that way we can use lookup_building_with_geo elsewhere, if needed

    only looking for *one* building...
    multiple matches can be found and returned elsewhere

    if this is made from a web request, pass the request in so we can log source
    """

    #rentrocket.helpers.address_search
    result = address_search(query, unit)
    if not result.errors:
        lookup_building_with_geo(result, make=make, request=request)
        
    return result

    ## (search_options, error, unit) = address_search(query)
    ## if not error:
    ##     (building, unit, error) = lookup_building_with_geo(search_options, unit_search=unit, make=make, request=request)
        
    ## return (building, unit, error, search_options)    
    
def find_by_tags(city_tag, bldg_tag, unit_tag='', default_unit=True):
    """
    this is a common task for locating a building or unit
    after a url request with specific tags
    abstracting here so it can be re-used for those calls
    """
    city = None
    building = None
    unit = None

    cities = City.objects.filter(tag=city_tag)
    if cities.count():
        city = cities[0]

    #old way... this doesn't work very reliably:
    #address = re.sub('_', ' ', bldg_tag)
    #buildings = Building.objects.filter(city=city).filter(address=address)
    buildings = Building.objects.filter(city=city).filter(tag=bldg_tag)
    if buildings.count():
        building = buildings[0]
        
        if not building.units.count():
            #temporary fix for incomplete buildings (no units)
            
            #must have a building with no associated units...
            #may only have one unit
            #or others may have been incorrectly created as separate buildings
            #either way we can start by making a new unit here
            #(and then merging in any others manually)

            unit = Unit()
            unit.building = building
            unit.number = ''
            # don't want to set this unless it's different:
            #unit.address = building.address 

            unit.save()

        #this doesn't seem to match when unit_tag is none
        found = False
        if unit_tag:
            units = building.units.filter(tag=unit_tag)
            if units.count():
                unit = units[0]
                found = True
        elif not found and default_unit:
            for bldg_unit in building.units.all():
                if not bldg_unit.number:
                    unit = bldg_unit
                    found = True

        #might be a case where there is only one unit
        #but that unit has a name / apartment number associated with it
        #in that case, blank won't match, but we still want to return it
        if not found:
            if building.units.count() == 1:
                unit = building.units[0]
                found = True

        #however, other functions may not require a unit to be returned...
        #and may not specify one... not necessarily an error then.
        ## if not found:
        ##     #This is probably an error...
        ##     #should always return a unit, even if one is not specified
        ##     raise ValueError, "No unit found"
            
            
        
        #TODO:
        #not sure that this will work with unit_tag yet...
        #(unit, error, matches) = building.find_unit(unit_tag)
        #maybe above filter approach is sufficient (and more efficient?) here
        
    return (city, building, unit)



def tally_energy_total(building, source):
    """
    building is used to get the 'who_pays...' data
    source can be either a unit or a building
    depending on which average you want to tally
    """
    complete = True

    total = 0
    for opt in [ ('average_electricity', 'who_pays_electricity'),
                 ('average_gas', 'who_pays_gas'), ]:

        #TODO:
        #consider using building.heat_source_details
        #instead of or in addition to who_pays_gas."service not available"
        who_pays = getattr(building, opt[1])
        value = getattr(source, opt[0])
        if (who_pays == 'not_available'):
            # service is not available at the location... 
            # should only be the case with natural gas
            # won't affect complete status
            pass

        #5 is arbitrary...
        #trying to avoid someone putting in a fake low value
        elif value and value > 5:
            total += value
        else:
            complete = False

    if complete and total:
        #now that both units and buildings are tracking energy_average
        #can save it here if it is different
        if source.energy_average != total:
            source.energy_average = total
            source.save()

    return total, complete

class Building(models.Model, ModelDiffMixin):
    """
    an indivdual structure
    could be part of a larger Property object (as needed)

    https://docs.google.com/document/d/1mEvxQbJFr3l5tcEAqkPdl2qBVTsKWbLnE3xlfkCcf2g/edit#
    """

    #aka building_id
    #'id' is a built in function in python,
    #but should be ok to use as an attribute
    #this may get configured automatically as part of Django:
    #id = models.CharField(max_length=10, primary_key=True)

    parcel = models.ForeignKey(Parcel)

    #this is too general to fit with the Home Facts Data Standard
    #split version can be kept at the parcel level...
    #will only be one street number per building
    address = models.CharField(max_length=200)

    city = models.ForeignKey(City)

    #State where the property is located.
    #In the U.S. this should be the two-letter code for the state
    #not always set?
    #safer to rely on city.state:
    state = models.CharField(max_length=2)

    postal_code = models.CharField(max_length=10)

    latitude = models.FloatField()
    longitude = models.FloatField()

    #blank=True means not required

    #optional property name
    name = models.CharField(max_length=80, blank=True, default='')

    #Type of residential property:
    #( single family, duplex, multi-family, single room occupancy,  etc)
    #type = models.CharField(max_length=30, blank=True)
    TYPE_CHOICES = (
        ('apartment', 'Apartment'),
        ('duplex', 'Duplex'),
        #aka single family
        ('house', 'House'),
        #aka multi-family
        ('multiunit', 'Multi-Unit Building'),
        ('room', 'Room'),
        ('condo', 'Condo'),
        ('other', 'Other'),
        )
    type = models.CharField(max_length=30, choices=TYPE_CHOICES, default="", blank=True)


    #if getting data from unknown sources,
    #it may not always be a rental property
    #or, it may have been a rental at one point, but is not a rental now
    #might not want to hide it either, depending on situation
    #
    #this is defined under unit.status... can vary from unit to unit:
    #rental = models.BooleanField(default=True)

    #eventually can use this to hide results
    visible = models.BooleanField(default=True)


    
    #this could also be a property of
    #how many Units are associated with the building
    #(but that may be inaccurate)
    number_of_units = models.IntegerField(default=0)

    #Year building was constructed or rebuilt.
    built_year = models.IntegerField(default=0)
    #Recorded building square feet 
    sqft = models.IntegerField(default=0)

    #this is the average size of all units in the building...
    #used in calculating energy scores
    average_sqft = models.FloatField(default=0)
    #alternatively, if we have the total sqft for the building (self.sqft)
    #could divide that by the number of units

    #Current assessed property value.
    value = models.FloatField(default=0)

    #might be better to keep this with the property manager
    #but making it here just in case
    website = models.CharField(max_length=200, blank=True)



    #RENT STATS
    #these should all be updated when a unit or listing changes, or nightly

    #for all units, regardless of available listings:
    #these should not both be set if they are equal... leave one set to zero
    max_rent = models.FloatField(default=0)
    min_rent = models.FloatField(default=0)

    #number of active listings
    active_listings = models.IntegerField(default=0)
    
    #max listing price
    #min listing price
    max_rent_listing = models.FloatField(default=0)
    min_rent_listing = models.FloatField(default=0)



    #who pays utilities:
 
    WHO_PAYS_CHOICES = (
        ('unknown', 'Unknown'),
        ('tenant', 'The tenant pays this bill directly to the utility.'),
        ('tenant_via_landlord', 'The landlord pays this bill and passes the costs to the tenant.'),
        ('landlord', 'The rent includes this service (i.e. the charge to the tenant does not vary by month).'),
        ('not_available', 'The service is not available at this location.'),
        ('other', 'Other'),
        )

    #break down by type
    who_pays_electricity = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")
    who_pays_gas = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")
    who_pays_water = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")
    who_pays_trash = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")
    who_pays_internet = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")
    who_pays_cable = models.CharField(max_length=20, choices=WHO_PAYS_CHOICES, default="unknown")

    #building wide averages:
    #specific details should be stored with units via utility models 
    #average utility cost ($) per month (over 1 year) for each type: 
    average_electricity = models.FloatField(default=0)
    average_gas = models.FloatField(default=0)
    average_water = models.FloatField(default=0)
    average_trash = models.FloatField(default=0)
    
    #average for all utilities, only ones that tenant pays
    #and only essentials (gas, electric, water, trash)
    total_average = models.FloatField(default=0) 
    
    #then add utilities (if tenant pays) to come up with estimated_totals
    #these can help when search for a specific total price range    
    estimated_total_min = models.FloatField(default=0)
    estimated_total_max = models.FloatField(default=0)
    #similar estimated for listing min and max?
    #or should these just be property values?

    #only gas and electric included here:  (use this / sqft for energy score)
    energy_average = models.FloatField(default=0)
    
    #regardless of who pays utilities, 
    #once we have energy data,
    #we will want to summarize the results here
    #so that we can use this to color code appropriately
    energy_score = models.FloatField(default=0)

    #when utility data was last updated (age of data)
    utility_data_updated = models.DateTimeField(blank=True, null=True)

    #many of these were adapted from google document form available at:
    #https://docs.google.com/forms/d/1qaJ26psJvY9DtBVfYXPUq_MZH6NINFKnbb-X_LbYiXI/formResponse

    #these will usually happen on a building level

    #http://en.wikipedia.org/wiki/Category:Heaters
    HEAT_SOURCE_CHOICES = (
        ('gas', 'Natural Gas'),
        ('electric', 'Electricity'),
        ('radiators', 'Radiators'),
        ('other', 'Other'),
        ('unknown', 'Unknown'),
        )
    heat_source_details = models.CharField(max_length=20, choices=HEAT_SOURCE_CHOICES, default='unknown', blank=True)
    heat_source_other = models.CharField(max_length=255, default='', blank=True)

    #Does the property include any of the following energy-saving features?
    energy_saving_features = models.BooleanField(default=False)
    ENERGY_SAVING_CHOICES = (
        ('appliances', 'Energy Star appliances'),
        ('lighting', 'Energy-efficient lighting (fluorescent or LED)'),
        ('windows', 'Well-sealed, double-paned windows or storm windows'),
        ('insulation', 'Good insulation (attic and walls insulated) and few air leaks (around doors/windows etc.)'),

        )
    #energy_improvements = models.TextField()
    #energy_improvements = JSONField(blank=True)
    energy_saving_details = MultiSelectField(max_length=100, choices=ENERGY_SAVING_CHOICES, default='', blank=True)
    energy_saving_other = models.CharField(max_length=255, default='', blank=True)

    RENEWABLE_CHOICES = (
        ('solar', 'Solar (electric or hot water)'),
        ('geothermal', 'Geothermal/heat pumps'),
        #('', ''),
        #('', ''),
        )
    renewable_energy = models.BooleanField(default=False)
    #renewable_energy_details = JSONField(default='""')
    renewable_energy_details = MultiSelectField(max_length=100, choices=RENEWABLE_CHOICES, default='', blank=True)
    renewable_energy_other = models.CharField(max_length=255, default='', blank=True)



    #smart-living:

    #for everything else...
    #anything here will not be available as a filter...
    #if there is a common addition that should be part of filter,
    #make a separate field
    smart_living = models.TextField(blank=True)

    #if these are available, they'll be available for the whole building:
    composting = models.BooleanField(default=False)
    recycling = models.BooleanField(default=False)

    #Does the unit have access to outdoor space for gardening?
    garden = models.BooleanField(default=False)
    GARDEN_CHOICES = (
        ('balcony', 'Balcony'),
        ('porch', 'Porch'),
        ('yard', 'Yard'),
        )

    #garden_details = JSONField(default='""')
    garden_details = MultiSelectField(max_length=100, choices=GARDEN_CHOICES, default='', blank=True)
    garden_other = models.CharField(max_length=255, default='', blank=True)
    #seems like community garden doesn't relate specific to property...
    #leaving it out
    #Community garden

    #may want to determine this based on other metrics
    #other metrics need to be defined before they can be stored in database
    #but for now, this is the distilled result
    bike_friendly = models.BooleanField(default=False)
    BIKE_CHOICES = (
        ('ample_parking', 'Ample bike parking - can find a space when you need one'),
        ('covered_parking', 'Covered bike parking'),
        ('bike_lockers', 'Bike lockers or other bike storage'),
        ('infrastructure_access', 'Easy access to bike infrastructure (bike lanes, trails, etc.)'),
        ('well_maintained', 'On-site bike facilities are maintained and accessible regardless of weather'),
        ('encouraged', 'Management encourages residents to bike'),
        )    
    bike_friendly_details = MultiSelectField(max_length=200, choices=BIKE_CHOICES, default='', blank=True)
    #bike_friendly_details = JSONField(default='""')
    bike_friendly_other = models.CharField(max_length=255, default='', blank=True)
  
    walk_friendly = models.BooleanField(default=False)
    WALK_CHOICES = (
        ('onsite_infrastructure', 'On-site sidewalks and other facilities make it easy to walk around'),
        ('offsite_access', 'Easy access to off-site sidewalks and other pedestrian infrastructure'),
        ('infrastructure_maintenance', 'On-site sidewalks and other pedestrian facilities are maintained and accessible regardless of weather'),
        ('encouraged', 'Management encourages residents to walk'),
        )
    #walk_friendly_details = JSONField(default='""')
    walk_friendly_details = MultiSelectField(max_length=200, choices=WALK_CHOICES, default='', blank=True)
    walk_friendly_other = models.CharField(max_length=255, default='', blank=True)

    transit_friendly = models.BooleanField(default=False)
    TRANSIT_CHOICES = (
        ('access', 'Easy access to transit stop(s) from the unit'),
        ('shuttle', 'Shuttle service provided by management'),
        ('encouraged', 'Management encourages residents to use public transit'),
        )
    #transit_friendly_details = JSONField(default='""')
    transit_friendly_details = MultiSelectField(max_length=100, choices=TRANSIT_CHOICES, default='', blank=True)
    transit_friendly_other = models.CharField(max_length=255, default='', blank=True)

    #cache this locally (similar to GPS)
    #these are from walkscore.com:
    walk_score = models.IntegerField(default=0)
    bike_score = models.IntegerField(default=0)
    transit_score = models.IntegerField(default=0)
     


    #amenities
    #old version:
    #air_conditioning = models.BooleanField(default=False)
    AC_CHOICES = (
        ('central', 'Central A/C'),
        ('window', 'Window A/C'),
        ('other', 'Other'),
        ('', 'None'),
        )
    air_conditioning = models.CharField(max_length=50, choices=AC_CHOICES, default="", blank=True)


    #laundry = models.BooleanField(default=False)
    #laundry = models.CharField(max_length=50, default='')
    LAUNDRY_CHOICES = (
        ('in_unit', 'Washer/dryer in unit'),
        ('hookups', 'Washer/dryer hook-up in unit'),
        ('building', 'Washer/dryer in building'),
        ('', 'None'),
        )
    laundry = models.CharField(max_length=50, choices=LAUNDRY_CHOICES, default="", blank=True)

    #parking = models.BooleanField(default=False)
    #parking = models.CharField(max_length=50, default='')
    PARKING_CHOICES = (
        ('offstreet', 'Off-street'),
        ('onstreet', 'On-street'),
        ('garage', 'Garage'),
        ('assigned', 'Assigned'),
        ('other', 'Other'),
        )
    parking_options = MultiSelectField(max_length=100, choices=PARKING_CHOICES, default='', blank=True)

    #generally, are pets allowed? details for this should go in lease
    pets = models.BooleanField(default=False)
    #switching to string to allow description:
    #pets = models.CharField(max_length=50, default='')
    #pets = models.CharField(max_length=10, choices=CYCLE_CHOICES, default="month")
    PET_CHOICES = (
        ('cats', 'Cats'),
        ('dogs', 'Dogs'),
        #('', ''),
        #('', ''),
        )
    pets_options = MultiSelectField(max_length=100, choices=PET_CHOICES, default='', blank=True)
    pets_other = models.CharField(max_length=255, default='', blank=True)
    
    gym = models.BooleanField(default=False)
    pool = models.BooleanField(default=False)
    game_room = models.BooleanField(default=False)
    #for everything else...
    #anything here will not be available as a filter...
    #if there is a common addition that should be part of filter,
    #make a separate field
    amenities = models.TextField(blank=True)
    
    #this is now a separate object/table for many to many join
    #aka BuildingPerson
    #that specifies the relationship of a person to a building
    #owner_name = models.CharField(max_length=50)
    #owner_mailing_address = models.CharField(max_length=50, blank=True)

    #google, bing, etc
    geocoder = models.CharField(max_length=10)

    #aka feed_source:
    #would like to leave this null if it's from the web
    source = models.ForeignKey(Source, blank=True, null=True)

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    #unfortunately this doesn't work
    #tag = models.CharField(max_length=200, default=to_tag(str(address)))
    tag = models.CharField(max_length=200, default='')


    def set_booleans(self):
        """
        #update any summary boolean fields here
        #(this should help with searching)
        """
        if self.energy_saving_details or self.energy_saving_other :
            self.energy_saving_features = True
        else:
            self.energy_saving_features  = False

        if self.renewable_energy_details or self.renewable_energy_other :
            self.renewable_energy = True
        else:
            self.renewable_energy = False

        if self.garden_details or self.garden_other:
            self.garden = True
        else:
            self.garden = False

        if self.bike_friendly_details or self.bike_friendly_other :
            self.bike_friendly = True
        else:
            self.bike_friendly = False

        if self.walk_friendly_details or self.walk_friendly_other :
            self.walk_friendly = True
        else:
            self.walk_friendly = False

        if self.transit_friendly_details or self.transit_friendly_other :
            self.transit_friendly = True
        else:
            self.transit_friendly = False

        if self.parking_options:
            self.parking = True
        else:
            self.parking = False

        if self.pets_options or self.pets_other :
            self.pets = True
        else:
            self.pets = False

        #saving is left to caller

    def update_rent_details(self):
        """
        call this after update utility averages
        that way most recent totals can be applied to estimated total

        TODO:
        similar function to update listing price ranges
        ...
        or maybe just show the estimate when looking at the actual listing
        """
        
        #for all units, regardless of available listings:
        #these should not both be set if they are equal... leave one set to zero
        #max_rent = models.FloatField(default=0)
        #min_rent = models.FloatField(default=0)

        building_values = {}
        first = True
        for unit in self.units.all():
            if unit.rent:
                if first:
                    #reset both of them:
                    self.max_rent = unit.rent
                    self.min_rent = unit.rent
                    first = False
                else:
                    if unit.rent > self.max_rent:
                        self.max_rent = unit.rent
                    if unit.rent < self.min_rent:
                        self.min_rent = unit.rent

        if self.max_rent == self.min_rent:
            #zero out one of the values,
            #so they aren't both displayed on the template
            self.min_rent = 0

        ## #then add utilities (if tenant pays) to come up with estimated_totals
        ## #these can help when search for a specific total price range    
        if self.total_average and self.max_rent:
            self.estimated_total_max = self.max_rent + self.total_average

        if self.total_average and self.min_rent:
            self.estimated_total_min = self.min_rent + self.total_average

        self.save()

        
    
    def update_utility_averages(self):
        """
        go through all associated units
        calculate the average utility cost for each type of service
        and store that in the corresponding local variable
        """
        average_types = ['average_electricity', 'average_gas', 'average_water', 'average_trash', 'sqft', 'energy_average', 'energy_score']
        #group all valid (non-zero) values by type
        building_values = {}
        for unit in self.units.all():
            for average_type in average_types:

                #now that units have real utility data,
                #could update those averages here
                #however, that might get intensive for buildings with many units
                #it's best to update the specific unit being modified
                #(can only modify one at a time anyway)
                #then this would work the same way
                #see unit.update_averages()
                
                value = getattr(unit, average_type)
                #only want to compute the average for units with values
                if value:
                    #rather than checking if key exists in dictionary:
                    #(or using a defaultdict)
                    building_values.setdefault(average_type, []).append(value)

        #special case for energy_scores...
        #get rid of all '.0001' (incomplete) values
        if building_values.has_key('energy_score'):
            filtered = []
            for value in building_values['energy_score']:
                if value != .0001:
                    filtered.append(value)

            if len(filtered):
                building_values['energy_score'] = filtered
            else:
                del building_values['energy_score']
                
        #then compute the average_value for each type with valid values
        #for key in building_values.keys():
        for key in average_types:
            if building_values.has_key(key):
                total = sum(building_values[key])
                average_value = total * 1.0 / len(building_values[key])
            else:
                #set it back to zero, incase invalid values were removed:
                average_value = 0

            #special case for sqft... 
            if key == 'sqft':
                setattr(self, 'average_sqft', average_value)
            else:
                setattr(self, key, average_value)


        #now that the averages have been tallied (as best as possible)
        #update other values that depend on those:

        #assume we have everything, until we find a missing value
        complete = True
        total = 0
        for opt in [ ('average_electricity', 'who_pays_electricity'),
                     ('average_gas', 'who_pays_gas'),
                     ('average_water', 'who_pays_water'),
                     ('average_trash', 'who_pays_trash'), ]:

            #this is appropriate for 'total_average' utility cost for a tenant
            #which will factor in to cost of rent
            #
            #should *NOT* be used as an indicator
            #of how efficient the property is
            #for that, use tally_energy_total and update energy_score below
                        
            who_pays = getattr(self, opt[1])
            if ((who_pays == 'tenant_via_landlord') or
                (who_pays == 'tenant')):
                #5 is arbitrary...
                #want to skip zero values
                #also trying to avoid someone putting in a fake low value
                value = getattr(self, opt[0])
                if value > 5:
                    total += value
                else:
                    #only marking things as incomplete
                    #if they are designated as being paid by tenant
                    #but the amount is not available.
                    complete = False

        #only storing total_average if it's complete 
        if complete:
            self.total_averge = total
        else:
            self.total_averge = 0




        #doing this as part of the averages above:
        #self.update_energy_score()

        #old approach for update_energy_score() at building level:
        #other functionality moved out to Unit.update_energy_score()
        
        ## if self.energy_average and self.average_sqft:
        ##     cost_per_sqft = self.energy_average * 1.0 / self.average_sqft
        ##     #want lower (better) values to have higher score
        ##     #that way can sort by score, higher ones show up first
        ##     self.energy_score = max_utility_cost / cost_per_sqft
        
        #could check for self.sqft value
        #divide by number of units for alternative to self.average_sqft
        #(especially if self.average_sqft is not available)

        #use model diff to help:
        if self.has_changed:
            self.save()
        
    def cost_per_sqft(self):
        cost_per_sqft = 0
        if self.energy_average and self.average_sqft:
            cost_per_sqft = self.energy_average * 1.0 / self.average_sqft
        return cost_per_sqft


    #either need to track average_bedrooms in building (good for summaries?)
    #or just run through all units 
    #and average each of their cost_per_bedrooom values
    #waiting to see if this is needed...
    #it is currently estimated as part of energy_score... that may suffice
    
    ## def cost_per_bedroom(self):
    ##     cost_per_bedroom = 0
    ##     if self.energy_average and self.average_bedrooms:
    ##         cost_per_bedroom = total * 1.0 / self.average_bedrooms
    ##     return cost_per_bedroom


    def create_tag(self, force=False):
        if ((not self.tag) and self.address) or force:
            #update stored tag so it also exists
            self.tag = to_tag(self.address)
            self.save()
            
        #either it exists or it won't
        return self.tag

    def url(self):
        """
        better to use reverse lookup here:
        """
        ### old way
        #tag = self.create_tag()
        #return "/building/" + tag + '/' + self.city.tag
        return reverse('building.views.details', args=(self.tag, self.city.tag))

    def find_unit(self, unit):
        """
        even with normalization, it is possible that the unit number
        doesn't match
        (maybe after entries created with google's #___ format are cleaned?)
        go through each of our units and see if the suffix is the same
        """
        if unit:
            suffix = unit.split()[-1]
            suffix = suffix.replace('#', '')
        else:
            suffix = ''

        error = None
        matches = []
        for unit in self.units.all():
            if unit.number:
                usuffix = unit.number.split()[-1]
                usuffix = usuffix.replace('#', '')
            else:
                usuffix = ''

            #print "Checking if ->%s<- == ->%s<-" % (usuffix, suffix)
            if usuffix == suffix:
                matches.append(unit)

        if len(matches) > 1:
            return (None, "More than one matching unit found. This shouldn't happen!", matches)
        elif len(matches) < 1:
            #this is not an error case...
            return (None, '', matches)
        else:
            return (matches[0], '', matches)

class Unit(models.Model, ModelDiffMixin):
    """
    an indivdual dwelling or unit
    can be part of a larger Building,
    or a Building might only have one Unit (1 to 1)
    """
    building = models.ForeignKey(Building, related_name="units")

    #these are duplicated on the building
    #so not strictly D.R.Y.
    #however, keeping a copy of this here will facilitate map searches
    #especially with the filter...
    #filtering should probably switch to showing results on map as units
    latitude = models.FloatField(default=0)
    longitude = models.FloatField(default=0)

    #isn't the version on building sufficient??
    #it's not, especially in the case of multiple units in one building
    #each with a different street number
    #can continue to use the building address in the url
    #even if sections are duplicated here:
    #only use it if it differs from building (do not use if the same!)
    address = models.CharField(max_length=200, blank=True, default='')

    #should be able to use this with the building.address (property)
    #to arrive at the unit.address:
    #this is the main ID for a unit
    number = models.CharField(max_length=20)

    #tag should be able to accomodate address *AND* number,
    #so it should be longer than just 20
    #this is only used in urls and looking up units based on the url's unit_tag
    #it is formed as a combination of number, and address if applicable
    tag = models.CharField(max_length=255, default='')

    #this is more for noting that a property is no longer going to be available
    #similar to setting building to not visible, but gives a reason...
    #not necessary to use if it's redundant
    #rented, owner-occupied, available, off the market
    STATUS_CHOICES = (
        ('unknown', 'Unknown'),
        ('rented', 'Rented'),
        ('owner-occupied', 'Owner-Occupied'),
        ('available', 'Available'),
        ('off-the-market', 'Off the market'),
        ('other', 'Other'),
        )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='unknown', blank=True)

    #eventually can use this to hide results
    visible = models.BooleanField(default=True)

    #-1 for studio
    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)

    sqft = models.IntegerField(default=0)

    #if 0, unknown
    #-1 = basement
    floor = models.IntegerField(default=0)

    #number of adults (can be used to help calculate cost per resident)
    max_occupants = models.IntegerField(default=0)

    #use this to track rents after we have a listing
    #this way we can give an estimate of the rent
    #aka current_rent
    rent = models.FloatField(default=0)

    #keeping a copy of this here, to assist with filtering...
    #don't want to need to join on listing objects when filtering...
    #will already need to join for building details
    listing_available = models.DateTimeField(blank=True, null=True)
    listing_rent = models.FloatField(default=0)

    #this is duplicated in a Listing:
    #deposit = models.FloatField(default=0)
    
    #allow photos *(more than 1)* to be submitted for the listing
    #photos and floor plans will be handled by:
    #BuildingPhoto and BuildingDocument

    #unit specific averages:
    #average utility cost ($) per month (over 1 year) for each type:
    #eventually these should be calculated from uploaded energy data
    #for now they can be specified manually
    average_electricity = models.FloatField(default=0)
    average_gas = models.FloatField(default=0)
    average_water = models.FloatField(default=0)
    average_trash = models.FloatField(default=0)

    #monthly details should be stored via associated utility models 
    #along with mins and maxes
    #what were the highest and lowest values in a given period
    #energy_max
    #energy_min
    #when utility details are updated, call self.update_averages

    #storing these here, even if they're redundant
    #potential for data loss if this is the only place they're stored
    #(subsequent updates from utility data could over-write)
    electricity_min = models.FloatField(default=0)
    electricity_max = models.FloatField(default=0)
    gas_min = models.FloatField(default=0)
    gas_max = models.FloatField(default=0)

    #these are the same as in Building, but specific to this unit
    
    #only gas and electric included here:  (use this / sqft for energy score)
    energy_average = models.FloatField(default=0)
    
    #regardless of who pays utilities, 
    #once we have energy data,
    #we will want to summarize the results here
    #so that we can use this to color code appropriately
    energy_score = models.FloatField(default=0)
    
    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    class Meta:
        ordering = ['number']

    def __repr__(self):
        temp_d = copy.copy(self.__dict__)        
        return str(temp_d)

    def cost_per_sqft(self):
        #total, complete = tally_energy_total(building, source)
        total, complete = tally_energy_total(self.building, self)

        cost_per_sqft = 0
        if total and self.sqft:
            cost_per_sqft = total * 1.0 / self.sqft
        return cost_per_sqft

    def cost_per_bedroom(self):
        total, complete = tally_energy_total(self.building, self)

        cost_per_bedroom = 0
        if total and self.bedrooms:
            #handle studios:
            if self.bedrooms == -1:
                cost_per_bedroom = total * 1.0 / (self.bedrooms * -1)
            else:
                cost_per_bedroom = total * 1.0 / self.bedrooms
                
        return cost_per_bedroom

    def update_energy_score(self, bedrooms=True):
        """
        this functionality was originally part of:
        building.update_utility_averages

        if keeping track of this on a unit level, can take care of it here.

        two main ways to generate a score...
        based on number of bedrooms or the total squarefeet
        
        it is important to be consistent in the system
        we're going with bedrooms in hopes that it is more intuitive and
        also easier to get that information

        regardless of who pays utilities, 
        once we have energy data,
        we will want to summarize the results in self.energy_score
        so that we can use this to color code appropriately
        #energy_score = models.IntegerField(default=0)

        it shouldn't matter who pays for it
        only the ammount used
        and for that, we probably only need to look at gas + electric
        the only time that gas can be skipped is if the heat type != gas        

        only gas and electric included here:
        (use this / sqft for energy score)
        #energy_average = models.FloatField(default=0)
        
        updating self.energy_average is handled in tally_energy_total now
        #self.energy_average = total
        """

        #keep this around to see if we need to call save or not:
        original_energy_score = self.energy_score
        
        #NOW CALCULATE ENERGY SCORE:

        #want lower (better) values to have higher score
        #that way can sort by score, higher ones show up first
        #divide max_utility_cost with actual value to invert

        #max cost will vary based on what the units are
        #could be lower for sqft vs bedrooms
        #ideally this is the maximum possible cost anywhere
        #so all scores end up comparable / related
        #keep as float:
        max_utility_cost = 500.0

        #tally_energy_total() will get called
        #in both self.cost_per_bedroom() and self.cost_per_sqft()
        #but we need to know if a total was found here, so duplicating the call
        
        #total, complete = tally_energy_total(building, source)
        #total, complete = tally_energy_total(self, self)
        total, complete = tally_energy_total(self.building, self)

        if complete and total:
            if bedrooms:
                cpbr = self.cost_per_bedroom()
                if cpbr:
                    self.energy_score = max_utility_cost / cpbr
                else:
                    self.energy_score = .0001
            else:
                #must be using sqft
                #might want to print a warning though!
                cpsqft = self.cost_per_sqft()
                if cpsqft:
                    self.energy_score = max_utility_cost / cpsqft
                else:
                    self.energy_score = .0001

        elif total:
            #using this to signal that we have some data, but it is incomplete
            self.energy_score = .0001
        else:
            self.energy_score = 0

        #trying to only do this if something has changed...
        #hoping that improves performance for bulk updates
        if self.energy_score != original_energy_score:
            self.save()

    def update_averages(self):
        """
        go through all associated utility statements
        parse the most recent year's worth of data for each type of service
        generate an average for each,
        and store that in the corresponding local variable
        """
        for utility_type in UTILITY_TYPES:
            #TODO:
            #ideally see if we have a complete year's worth of data...
            #if so, that should take priority

            #but for now... just average everything that is there

            #query = UtilitySummary.objects.filter(building=building, unit=unit, type=utility_type[0])
            #print dir(self)
            #print "checking type: %s" % utility_type[0]
            query = self.utilitysummary_set.filter(type=utility_type[0])

            updated = False
            
            #print "found: %s items" % len(query)
            if len(query):
                #print "HAVE DATA!"
                count = 0
                total = 0

                #TODO:
                #keep track of mins and maxes for assignment later
                #not sure if we want to update the values yet...
                #they were used to store data
                #that didn't have anywhere else to go at the time
                cur_max = 0
                cur_min = 9999999
                
                for summary in query:
                    if summary.cost:
                        total += summary.cost
                        count += 1
                        if summary.cost > cur_max:
                            cur_max = summary.cost
                        if summary.cost < cur_min:
                            cur_min = summary.cost

                if count:
                    average = total * 1.0 / count
                else:
                    average = 0

                print "calculated average for %s to be: %s" % (utility_type[0], average)
                #don't overwrite with 0?
                if average:
                    if utility_type[0] == 'gas':
                        self.average_gas = average
                        updated = True
                    elif utility_type[0] == 'electricity':
                        self.average_electricity = average
                        updated = True
                    elif utility_type[0] == 'water':
                        self.average_water = average
                        updated = True
                    elif utility_type[0] == 'trash':
                        self.average_trash = average
                        updated = True
                    #not yet tracked:
                    ## elif utility_type[0] == 'sewage':
                    ## elif utility_type[0] == 'recycling':
                    ## elif utility_type[0] == 'other':
                    ## elif utility_type[0] == 'oil':

            if updated:
                self.save()
                
    def url_tag(self):
        """
        return tag encoded as a url string... often needed with '#' in tag

        might be better to just get rid of '#' in tags,
        since they cause such a mess in urls
        """
        return urlencode(self.tag)
    
    def unit_address(self):
        """
        check if we have an address or number set
        combine them accordingly

        does *NOT* include any address from the parent building.

        this is for getting the unique address of the unit only
        """
        if (self.address and self.number):
            full = "%s, %s" % (self.address.strip(), self.number)
            return full
        elif self.address:
            return self.address
        elif self.number:
            #by process of elimination, must just have a number
            return self.number
        else:
            #must not have anything
            return ""

    def full_address(self):
        """
        when we want the combination of a building and unit address

        in an extreme case, this could be long and unweildy

        e.g. a building contains many different street numbers
        and the unit has it's own street number
        the full address could end up as:
        100-200 East Main Street, 142 East Main Street

        just be smarter about it...
        if we have self.address, don't use building address
        """
        if self.address:
            return self.unit_address()
        elif self.number:
            full = "%s, %s" % (self.building.address.strip(), self.number)
            return full
        else:
            return self.building.address.strip()

    def full_address_with_link(self):
        """
        similar to full_address, but link to the main building
        could be more verbose.
        """
        if self.number:
            
            full = '<a href="%s">%s</a>, %s' % (self.building.url(), self.building.address.strip(), self.number)
        else:
            full = '<a href="%s">%s</a>' % (self.building.url(), self.building.address.strip())
        return full

        
    def create_tag(self, force=False):
        if (not self.tag and (self.address or self.number)) or force:
            #update stored tag so it also exists
            self.tag = to_tag(self.unit_address())
            self.save()
            
        #either it exists or it won't
        return self.tag
    
        
    def save_and_update(self, request):
        """
        there are now many steps to saving a unit 
        and updating related fields...
        wrapping these up in a single call

        changes should have already been applied to the Unit before calling this
        """
        #print json.dumps(updated.diff)

        if self.get_field_diff('rent'):
            #rent has been changed... add a new entry to rent history
            rh = RentHistory()
            rh.rent = self.rent
            rh.unit = self
            rh.save()

        #print self.diff
        changes = ChangeDetails()
        changes.ip_address = get_client_ip(request)

        #with simple form, may have an anonymous user, in which case, ignore
        if request.user and not request.user.is_anonymous and request.user.is_authenticated:
            #print request.user
            #print type(request.user)
            #print dir(request.user)
            changes.user = request.user
        changes.diffs = json.dumps(self.diff)
        changes.building = self.building
        #not required
        changes.unit = self
        changes.save()

        #now it's ok to save the unit details:
        self.save()

        #may not need to do this every time,
        #but certainly need to do it if any utility summaries have been updated
        self.update_averages()

        #see if we have enough info now to make a score:
        self.update_energy_score()
        
        #now that we've saved the unit,
        #update the averages for the whole building:
        self.building.update_utility_averages()
        self.building.update_rent_details()
            

class RentHistory(models.Model):
    """
    Place to keep track of older rent values for a given unit
    """
    rent = models.FloatField(default=0)
    unit = models.ForeignKey(Unit, related_name="rent_history")
    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)
    #not sure if we'll want to keep this here, or just with ChangeDetails
    #ip_address = models.GenericIPAddressField(blank=True, null=True)


class BuildingDocument(models.Model):
    """
    object to represent uploaded data for a building

    These should not be photo content
    more for downloading

       - lease agreement
       - application forms
    
    """
    #if a file (statement) was uploaded, this is where it will be stored:
    blob_key = models.TextField()

    #can use this when downloading file
    filename = models.CharField(max_length=50)

    description = models.TextField()

    #application, etc
    type = models.CharField(max_length=30, blank=True)

    #building = models.ForeignKey(Building)
    #unit = models.ForeignKey(Unit, blank=True, null=True)
    building = models.ForeignKey(Building, related_name="documents")
    unit = models.ForeignKey(Unit, related_name="documents", blank=True, null=True)
    #not sure that this makes sense
    #listing = models.ForeignKey(Listing, related_name="documents", blank=True, null=True)

    added = models.DateTimeField('date published', auto_now_add=True)

class BuildingPhoto(models.Model):
    """
    object to represent uploaded photo for a building

    these will show in the relevant photo sections
    """
    blob_key = models.TextField()

    #can use this when downloading file
    filename = models.CharField(max_length=50)

    description = models.TextField()

    #interior, exterior, floorplan, etc
    type = models.CharField(max_length=30, blank=True)

    building = models.ForeignKey(Building, related_name="photos")
    unit = models.ForeignKey(Unit, related_name="photos", blank=True, null=True)
    #not sure that this makes sense
    #listing = models.ForeignKey(Listing, related_name="documents", blank=True, null=True)

    added = models.DateTimeField('date published', auto_now_add=True)

class BuildingPerson(models.Model):
    """
    for storing relations between people and Buildings (and optionally Units)
    """

    building = models.ForeignKey(Building, related_name="people")
    person = models.ForeignKey(Person)
    #this is optional... may not be related to a single unit
    unit = models.ForeignKey(Unit, blank=True, null=True)
    #owner? renter? property manager? etc
    relation = models.CharField(max_length=50, default="Unknown")

    #allow renters to toggle whether their profile shows up on building details
    visible = models.BooleanField(default=True)


class BuildingComment(models.Model):
    """
    a comment for a building
    """
    building = models.ForeignKey(Building, related_name="comments")
    #not required
    #unit = models.ForeignKey(Unit, related_name="changes", blank=True, null=True)
    message = models.TextField()

    user = models.ForeignKey(User)
    added = models.DateTimeField('date published', auto_now_add=True)
    
class ChangeDetails(models.Model):
    """
    A place to track changes made to a building or unit
    aka History
    """
    #original_values = JSONField()
    #new_values = JSONField()
    #can store both in one dict field
    diffs = JSONField(default="", blank=True)
    building = models.ForeignKey(Building, related_name="changes")
    #not required
    unit = models.ForeignKey(Unit, related_name="changes", blank=True, null=True)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, blank=True, null=True)

    #especially for marking something as not visible, should note why
    note = models.CharField(max_length=255, default='', blank=True)

    added = models.DateTimeField('date published', auto_now_add=True)
    

class UnitType(models.Model):
    """
    some buildings may have many units of a similar type

    this could be expanded to allow those details to be grouped
    """
    pass
    
class Permit(models.Model):
    """
    for storing details about the rental permit source
    """
    pass

