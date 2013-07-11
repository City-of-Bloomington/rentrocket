from django.db import models

from building.models import Building, Unit
from source.models import Source


class Service(models.Model):
    """
    AKA Reading

    A summary of utility service received for a given address.

    adapted from:
    https://docs.google.com/document/d/1bwcGTgGkdnu8LjjYiyg6YBocwdzEsk5mqeU9GhjW4so/edit?pli=1
    """

    #When exporting data for House Facts Data Standard, convert to following:
    #water, sewer, storm water, gas, electricity, trash, recycling, compost, data, video, phone, data+video, video+phone, data+phone, data+video+phone, wifi

    #It would be nice to keep the nomenclature common across cities for analytical purposes.

    SERVICE_CHOICES = (
        ('water', 'Water'),
        ('sewer', 'Sewer'),
        ('storm', 'Storm Water'),
        ('gas', 'Gas'),
        ('elect', 'Electricity'),
        ('trash', 'Trash'),
        ('recyc', 'Recycling'),
        ('compo', 'Compost'),
        ('data', 'Data'),
        ('video', 'Video'),
        ('phone', 'Phone'),
        ('dv', 'Data+Video'),
        ('video', 'Video+Phone'),
        ('dp', 'Data+Phone'),
        ('dvp', 'Data+Video+Phone'),
        ('wifi', 'Wifi'),
        )
    

    #
    #reading_id = number (required=yes)

    #
    #building_id = string (required=yes)
    building = models.ForeignKey(Building)

    #
    #parcel_id = string (required=no)

    #Required if reading is for specific unit in a multi-unit building.
    #A unit name or number is acceptable.
    #if every building has at least one unit, this is all that is needed.
    #probably easier to keep both though
    #unit_number = string (required=no)
    unit = models.ForeignKey(Unit)

    #source of report.
    #could be: city data, utility data, or crowd-sourced public reporting
    #reading_source = string (required=yes)
    source = models.ForeignKey(Source)

    #Date of the reading event in YYYY-MM-DD format.
    #reading_date = date (required=yes)
    added = models.DateTimeField('date published')

    #Start of the utility service billing period in YYYY-MM-DD format
    #reading_period_start_date = date (required=no)
    start_date = models.DateTimeField()

    #Last day of the utility service billing period in YYYY-MM-DD format
    #reading_period_end_date = date (required=no)
    end_date = models.DateTimeField()

    #One of the following categories (water, sewer, storm water, gas, electricity, trash, recycling, compost, data, video, phone, data+video, video+phone, data+phone, data+video+phone, wifi). It would be nice to keep the nomenclature common across cities for analytical purposes.
    #reading_type = string (required=yes)
    type = models.CharField(max_length=5, choices=SERVICE_CHOICES, default="elect")

    #Vendor for utility service. Examples: City of Bloomington Utilities, Comcast, AT&T, Duke Energy, etc)
    #vendor = string (required=no)
    vendor = models.CharField(max_length=200, blank=True)

    #Common units acceptable (gallon, liter, kW, lb, kg, etc)
    #reading_unit = string (required=yes)
    #aka increment
    #not going with "unit" to avoid confusion with a unit in a building
    unit_of_measurement = models.CharField(max_length=50)

    #Numerical value of reading (may need to consider other options like (on, off) for acceptable values
    #reading_value = number (required=yes)
    #aka value
    amount = models.FloatField()

    #Billing cost for utility consumption.
    #reading_cost = currency (required=no)
    cost = models.FloatField(blank=True)
