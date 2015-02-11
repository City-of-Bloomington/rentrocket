from django.db import models

from django.contrib.auth.models import User

from building.models import Building, Unit

# Create your models here.

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

    #these may be duplicated at the unit level:
    #aka rent?
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

