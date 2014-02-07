from django.db import models

from source.models import Source
from city.models import City
from person.models import Person
from rentrocket.helpers import to_tag

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

    #TODO:
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


class Building(models.Model):
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

    #TODO:
    #tag = models.CharField(max_length=200)
    
    city = models.ForeignKey(City)

    #State where the property is located.
    #In the U.S. this should be the two-letter code for the state
    state = models.CharField(max_length=2)

    postal_code = models.CharField(max_length=10)

    latitude = models.FloatField()
    longitude = models.FloatField()

    #Type of residential property:
    #( single family, duplex, multi-family, single room occupancy,  etc)
    #blank=True means not required
    type = models.CharField(max_length=30, blank=True)
    
    #this could also be a property of
    #how many Units are associated with the building
    #(but that may be inaccurate)
    number_of_units = models.IntegerField(default=0)

    #Year building was constructed or rebuilt.
    built_year = models.IntegerField(default=0)
    #Recorded building square feet 
    sqft = models.IntegerField(default=0)

    #Current assessed property value.
    value = models.FloatField(default=0)

    #cache this locally (similar to GPS)
    walk_score = models.IntegerField(default=0)

    #once we have energy data,
    #we will want to summarize the results here
    #so that we can use this to color code appropriately
    energy_score = models.IntegerField(default=0)

    #this should be a separate object/table for many to many join
    #aka BuildingPerson
    #that specifies the relationship of a person to a building
    #TODO: ForeignKey:
    #owner_name = models.CharField(max_length=50)
    #owner_mailing_address = models.CharField(max_length=50, blank=True)

    #google, bing, etc
    geocoder  = models.CharField(max_length=10)

    #aka feed_source:
    source = models.ForeignKey(Source)

    #visible = models.BooleanField(default=True)


    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    def to_dict(self):
        """
        return a simple dictionary representation of the building
        this is used by ajax calls to get a representation of the building
        (via views.lookup)
        """
        profile = '<a href="%s">%s</a>' % (self.url(), self.address)
        #result = {'address': self.address, 'lat': self.latitude, 'lng': self.longitude}
        result = {'address': self.address, 'lat': self.latitude, 'lng': self.longitude, 'profile': profile}
        return result

    def url(self):
        return "/building/" + self.tag() + '/' + self.city.tag

    def tag(self):
        return to_tag(self.address) 
    

class Unit(models.Model):
    """
    an indivdual dwelling or unit
    can be part of a larger Building,
    or a Building might only have one Unit (1 to 1)
    """
    building = models.ForeignKey(Building, related_name="units")

    address = models.CharField(max_length=200)

    #should be able to use this with the building.address (property)
    #to arrive at the unit.address:
    number = models.CharField(max_length=20)

    #store these locally for looking up nearby features
    #gps = models.CharField(max_length=200)
    #is building sufficient to store this in?
    #latitude = models.FloatField()
    #longitude = models.FloatField()

    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)

    sqft = models.IntegerField(default=0)

    #number of adults (can be used to help calculate cost per resident)
    max_occupants = models.IntegerField(default=0)
    
    #TODO:
    #foreign keys to photos and floor plans (via Content module)

    #allow photos *(more than 1)* to be submitted for the listing
    #but associate them with the unit
    #content_set

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)

    #TODO:
    #this should be stored to assist with lookups
    #same goes for Building
    def tag(self):
        return to_tag(self.number) 
    

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
    #TODO:
    #person = models.ForeignKey(Person)

    #TODO:
    #even though the building is available by way of the Unit
    #it may be easier to look at building
    #especially when limiting search results on a map
    #building = models.ForeignKey(Building, related_name="listings")
    

    #the unit available
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

    #TODO:
    #what utilities are included: (to help estimate total cost)
    #TODO:
    #this would also be a good place to collect energy data from users
    #should create corresponding entries in services fields

    #TODO:
    #application (to apply for lease)
    #link to a default one for manager if available
    #otherwise allow one to be attached?
    #application = models.ForeignKey(Content)

    #TODO:
    #allow photos *(more than 1)* to be submitted for the listing
    #but associate them with the unit

    added = models.DateTimeField('date published', auto_now_add=True)
    updated = models.DateTimeField('date updated', auto_now=True)


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

    #TODO:
    #allow renters to toggle whether their profile shows up on building details
    #visible = models.BooleanField(default=True)
    
class Permit(models.Model):
    """
    for storing details about the rental permit source
    """

    pass
