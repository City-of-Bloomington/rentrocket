from django.db import models

from source.models import Source

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

    ## Shape
    ## geometry
    ## Yes
    ## This field contains data that describes the boundaries of the lot. It is generated automatically when the shapefile is created and will display a type of polygon or multipolygon.
    shape = models.TextField()

    #aka feed_source:
    source = models.ForeignKey(Source)

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

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

    #Type of residential property:
    #( single family, duplex, multi-family, single room occupancy,  etc)
    #blank=True means not required
    type = models.CharField(max_length=12, blank=True)
    
    #this could also be a property of
    #how many Units are associated with the building
    #(but that may be inaccurate)
    number_of_units = models.IntegerField(default=0)

    #Year building was constructed or rebuilt.
    built_year = models.IntegerField()
    #Recorded building square feet 
    sqft = models.IntegerField()

    #Current assessed property value.
    value = models.FloatField()

    #this is too general to fit with the Home Facts Data Standard
    #address = models.CharField(max_length=200)

    #Lowest numerical value of the street number
    #if the building has an address range or only building street number.
    from_st = models.CharField(max_length=12)

    #Highest numerical value of the street number
    #if the building has an address range.
    to_st = models.CharField(max_length=12, blank=True)

    street = models.CharField(max_length=50)

    street_type = models.CharField(max_length=10)

    #State where the property is located.
    #In the U.S. this should be the two-letter code for the state
    state = models.CharField(max_length=10)

    postal_code = models.CharField(max_length=10)

    latitude = models.FloatField()
    longitude = models.FloatField()

    #TODO: ForeignKey:
    #owner_name = models.CharField(max_length=50)
    #owner_mailing_address = models.CharField(max_length=50, blank=True)

    #TODO: ForeignKey:
    #city = models.CharField(max_length=50)
    #city = models.ForeignKey(City)

    #aka feed_source:
    #source = models.ForeignKey(FeedInfo)
    source = models.ForeignKey(Source)

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

    

class Unit(models.Model):
    """
    an indivdual dwelling or unit
    can be part of a larger Building,
    or a Building might only have one Unit (1 to 1)
    """
    building = models.ForeignKey(Building)

    address = models.CharField(max_length=200)

    #should be able to use this with the building.address (property)
    #to arrive at the unit.address:
    number = models.CharField(max_length=10)

    #store these locally for looking up nearby features
    #gps = models.CharField(max_length=200)
    #is building sufficient to store this in?
    #latitude = models.FloatField()
    #longitude = models.FloatField()

    #TODO:
    #manager = models.ForeignKey(Manager)
    #manager = models.ForeignKey(Person)

    bedrooms = models.IntegerField(default=0)
    bathrooms = models.IntegerField(default=0)

    square_feet = models.IntegerField(default=0)

    #number of adults (can be used to help calculate cost per resident)
    max_occupants = models.IntegerField(default=0)
    
    #TODO:
    #foreign keys to photos and floor plans (via Content module)

    #allow photos *(more than 1)* to be submitted for the listing
    #but associate them with the unit
    #content_set

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

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

    #the unit available
    unit = models.ForeignKey(Unit)

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

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')
