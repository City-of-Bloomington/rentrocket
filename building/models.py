from django.db import models

from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

from jsonfield import JSONField

from source.models import Source
from city.models import City
from person.models import Person
from rentrocket.helpers import to_tag, MultiSelectField

from urllib import urlencode

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
    air_conditioning = models.BooleanField(default=False)

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
    source = models.ForeignKey(Source)

    #eventually can use this to hide results
    visible = models.BooleanField(default=True)

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    #unfortunately this doesn't work
    #tag = models.CharField(max_length=200, default=to_tag(str(address)))
    tag = models.CharField(max_length=200, default='')


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
        #group all valid (non-zero) values by type
        building_values = {}
        for unit in self.units.all():
            for average_type in ['average_electricity', 'average_gas', 'average_water', 'average_trash', 'sqft']:
                value = getattr(unit, average_type)
                if value:
                    #rather than checking if key exists in dictionary:
                    #(or using a defaultdict)
                    building_values.setdefault(average_type, []).append(value)
                    
        #then compute the average_value for each type with valid values
        for key in building_values.keys():
            total = sum(building_values[key])
            average_value = total * 1.0 / len(building_values[key])

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

            who_pays = getattr(self, opt[1])
            if ((who_pays == 'tenant_via_landlord') or
                (who_pays == 'tenant')):
                #5 is arbitrary...
                #trying to avoid someone putting in a fake low value
                value = getattr(self, opt[0])
                if value > 5:
                    total += value
                else:
                    complete = False

        #only storing total_average if it complete 
        if complete:
            self.total_averge = total
        else:
            self.total_averge = 0
    
        #only gas and electric included here:
        #(use this / sqft for energy score)
        #energy_average = models.FloatField(default=0)

        #assume we have everything, until we find a missing value

        #total, complete = tally_energy_total(building, source)
        total, complete = tally_energy_total(self, self)

        ## #regardless of who pays utilities, 
        ## #once we have energy data,
        ## #we will want to summarize the results here
        ## #so that we can use this to color code appropriately
        ## energy_score = models.IntegerField(default=0)

        if complete and total:
            self.energy_average = total
            if self.energy_average and self.average_sqft:
                cost_per_sqft = self.energy_average * 1.0 / self.average_sqft
                #want lower (better) values to have higher score
                #that way can sort by score, higher ones show up first
                self.energy_score = 100.0 / cost_per_sqft
            #TODO:
            #could check for self.sqft value
            #divide by number of units for alternative to self.average_sqft
            #(especially if self.average_sqft is not available)
        elif total:
            #using this to signal that we have some data, but it is incomplete
            self.energy_score = .0001
        else:
            self.energy_score = 0

        self.save()
        
    def cost_per_sqft(self):
        cost_per_sqft = 0
        if self.energy_average and self.average_sqft:
            cost_per_sqft = self.energy_average * 1.0 / self.average_sqft
        return cost_per_sqft

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

class Unit(models.Model, ModelDiffMixin):
    """
    an indivdual dwelling or unit
    can be part of a larger Building,
    or a Building might only have one Unit (1 to 1)
    """
    building = models.ForeignKey(Building, related_name="units")

    #isn't the version on building sufficient??
    #it's not, especially in the case of multiple units in one building
    #each with a different street number
    #can continue to use the building address in the url
    #even if sections are duplicated here:
    #only use it if it differs from building (do not use if the same!)
    address = models.CharField(max_length=200, blank=True, default='')

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

    #should be able to use this with the building.address (property)
    #to arrive at the unit.address:
    number = models.CharField(max_length=20)

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

    
    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    #tag should be able to accomodate address *AND* number,
    #so it should be longer than just 20
    tag = models.CharField(max_length=255, default='')

    class Meta:
        ordering = ['number']


    def cost_per_sqft(self):
        #total, complete = tally_energy_total(building, source)
        total, complete = tally_energy_total(self.building, self)

        cost_per_sqft = 0
        if total and self.sqft:
            cost_per_sqft = total * 1.0 / self.sqft
        return cost_per_sqft


    def url_tag(self):
        """
        return tag encoded as a url string... often needed with '#' in tag

        might be better to just get rid of '#' in tags,
        since they cause such a mess in urls
        """
        return urlencode(self.tag)
    
    def update_averages(self):
        """
        go through all associated utility statements
        parse the most recent year's worth of data for each type of service
        generate an average for each,
        and store that in the corresponding local variable
        """
        pass

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
    

class Listing(models.Model):
    """
    An option to lease, rent, or sublease a specific Unit
    """

    CYCLE_CHOICES = (
        ('year', 'Year'),
        ('month', 'Month'),
        ('week', 'Week'),
        ('day', 'Day'),
        )

    #who is listing the unit:
    #person = models.ForeignKey(Person)
    #might be better to just use a User account
    #this should be required (setting blank and null to assist with migrations)
    user = models.ForeignKey(User, blank=True, null=True)

    #even though the building is available by way of the Unit
    #it may be easier to look at building
    #especially when limiting search results on a map
    #
    #also, it may be better to schedule a nightly task to update/cache
    #the number of listings that are available in a building
    #otherwise that could be an expensive search
    #
    #this should be required (setting blank and null to assist with migrations)
    building = models.ForeignKey(Building, related_name="listings", blank=True, null=True)
    

    #the unit available
    #unit = models.ForeignKey(Unit, related_name="listings", blank=True, null=True)
    unit = models.ForeignKey(Unit, related_name="listings")

    #sublease, standard?
    lease_type = models.CharField(max_length=200, default="Standard")

    lease_term = models.CharField(max_length=200, default="12 Months")

    #optional
    available_start = models.DateTimeField()
    #might be useful for subleases:
    available_end = models.DateTimeField()

    active = models.BooleanField(default=True)
    
    cost = models.FloatField()
    cost_cycle = models.CharField(max_length=10, choices=CYCLE_CHOICES, default="month")
    deposit = models.FloatField()

    description = models.TextField()

    #are pets allowed? if so what kind?
    pets = models.CharField(max_length=200)

    #what utilities are included: (to help estimate total cost)
    #
    #this is set at the building level
    #should be consistent within a building,
    #and that makes things easier to read if it's not duplicated here:

    #TODO:
    #application (to apply for lease)
    #link to a default one for manager if available
    #otherwise allow one to be attached?
    #application = models.ForeignKey(BuildingDocument)

    #TODO:
    #allow photos *(more than 1)* to be submitted for the listing
    #but associate them with the unit

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)


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

