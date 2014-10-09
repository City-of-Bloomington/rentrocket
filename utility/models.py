from django.db import models
from django.contrib.auth.models import User

from building.models import Building, Unit
from source.models import Source
from person.models import Person

from jsonfield import JSONField

#When exporting data for House Facts Data Standard, convert to following:
#water, sewer, storm water, gas, electricity, trash, recycling, compost, data, video, phone, data+video, video+phone, data+phone, data+video+phone, wifi

#It would be nice to keep the nomenclature common across cities for analytical purposes.

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

class StatementUpload(models.Model):
    """
    object to represent an uploaded statement.
    This starts off as unprocessed data,
    and eventually gets converted into one or more
    corresponding UtilitySummary objects
    """

    #if a file (statement) was uploaded, this is where it will be stored:
    blob_key = models.TextField()

    #rather than use a ForeignKey, keep it as text
    #this way users can upload data for cities not in system yet
    #and we can gauge interest for the service in other cities.
    city_tag = models.CharField(max_length=150)

    #eventually duplicated in generated Utility objects
    #but if it is supplied at the time of the upload, can keep track of it here
    building_address = models.CharField(max_length=200)

    unit_number = models.CharField(max_length=20, blank=True, null=True)
    #just using strings, in case the supplied value is not in the database yet 
    #building = models.ForeignKey(Building, blank=True)
    #unit = models.ForeignKey(Unit, blank=True, null=True)  

    #track what IP address supplied the statement...
    #might help if someone decides to upload garbage
    #especially if logins are not required
    ip_address = models.GenericIPAddressField()

    added = models.DateTimeField('date published', auto_now_add=True)

    vendor = models.CharField(max_length=200, blank=True)

    type = models.CharField(max_length=12, choices=UTILITY_TYPES, default="electricity")


    #keep track of any unit details in an unprocessed upload here
    #eventually these should be added to the actual building/unit
    #
    #format as a json blob
    #include values such as:
    # - move in date (instead of months lived) DateField
    # - square feet of unit
    # - how many bedrooms
    # - programmable thermostat?
    #unit_details = models.TextField(blank=True)
    unit_details = JSONField(blank=True)

    #when the person moved in to the unit
    #eventually associate this with a BuildingPerson?
    move_in = models.DateField('move in date', blank=True, null=True)

    #this could go with the unit as well:
    #other energy sources:
    #list? text?
    energy_sources = JSONField(blank=True, null=True)
    
    #ways of saving energy at residence: (text)
    energy_strategy = models.TextField(blank=True, null=True)

    #if the person has logged in with an account at the time of upload,
    #capture that here
    user = models.ForeignKey(User, blank=True, null=True)

    #otherwise, if they provide an email address for future contact,
    #update that here:
    person_email = models.EmailField(max_length=200, blank=True, null=True)

    #processing (extracting and importing data) may need to happen separately:
    processed = models.BooleanField(default=False)



class UtilitySummary(models.Model):
    """
    AKA Reading, Service

    A summary of utility service received for a given address.

    adapted from:
    https://docs.google.com/document/d/1bwcGTgGkdnu8LjjYiyg6YBocwdzEsk5mqeU9GhjW4so/edit?pli=1

    this can also reference the original uploaded statement
    """

    #not going to require building and unit...
    #can set it if it is supplied through the app
    #or can go look it up later once the statement is processed (after upload)

    #in order for it to show up on a map, it will need to be set.
    
    #building_id = string (required=yes)
    building = models.ForeignKey(Building)

    #parcel_id = string (required=no)

    #Required if reading is for specific unit in a multi-unit building.
    #A unit name or number is acceptable.
    #if every building has at least one unit, this is all that is needed.
    #probably easier to keep both though
    #unit_number = string (required=no)
    unit = models.ForeignKey(Unit)

    #if this was taken from a statement, associate it here
    #(but it could be added directly via a form... manually add bill, etc)
    statement = models.ForeignKey(StatementUpload, blank=True)

    #source of report.
    #could be: city data, utility data, or crowd-sourced public reporting
    #reading_source = string (required=yes)
    #source = models.ForeignKey(Source)
    #would like to leave this null if it's from the web
    source = models.ForeignKey(Source, blank=True, null=True)

    #Date of the reading event in YYYY-MM-DD format.
    #reading_date = date (required=yes)
    added = models.DateTimeField('date published', auto_now_add=True)

    #Start of the utility service billing period in YYYY-MM-DD format
    #reading_period_start_date = date (required=no)
    start_date = models.DateTimeField()

    #Last day of the utility service billing period in YYYY-MM-DD format
    #to simplify data entry, will only require a start date...
    #can infer end date
    #reading_period_end_date = date (required=no)
    end_date = models.DateTimeField(blank=True)

    #One of the following categories (water, sewer, storm water, gas, electricity, trash, recycling, compost, data, video, phone, data+video, video+phone, data+phone, data+video+phone, wifi). It would be nice to keep the nomenclature common across cities for analytical purposes.
    #reading_type = string (required=yes)
    type = models.CharField(max_length=12, choices=UTILITY_TYPES, default="electricity")

    #Vendor for utility service. Examples: City of Bloomington Utilities, Comcast, AT&T, Duke Energy, etc)
    #vendor = string (required=no)
    vendor = models.CharField(max_length=200, blank=True)

    #Common units acceptable (gallon, liter, kW, lb, kg, etc)
    #reading_unit = string (required=yes)
    #aka increment
    #not going with "unit" to avoid confusion with a unit in a building
    unit_of_measurement = models.CharField(max_length=50, blank=True)

    #Numerical value of reading (may need to consider other options like (on, off) for acceptable values
    #reading_value = number (required=yes)
    #aka value
    amount = models.FloatField(blank=True)

    #Billing cost for utility consumption.
    #reading_cost = currency (required=no)
    cost = models.FloatField(blank=True)



