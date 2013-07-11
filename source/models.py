from django.db import models

from person.models import Person
#from manager.models import Manager


class FeedInfo(models.Model):
    """
    Details about a given Feed source

    Adapted from House Facts Data Standard:
    https://docs.google.com/a/codeforamerica.org/document/d/1mEvxQbJFr3l5tcEAqkPdl2qBVTsKWbLnE3xlfkCcf2g/edit?pli=1#
    """

    #Date this feed was generated in YYYY-MM-DD format
    #aka feed_date
    added = models.DateTimeField('date published')

    #Version of the OHHS specification used to generate this feed.
    #For example '0.1'
    #aka feed_version
    version = models.CharField(max_length=12)

    #Name of the municipality providing this feed.
    #For example 'San Francisco' or 'Multnomah County'
    municipality_name = models.CharField(max_length=20)

    #Describes how the municipality defines or creates the variable building_id
    #(convention for defining  building_id).
    building_id_definition = models.TextField()

    #Describes how the municipality defines or creates the variable parcel_id
    parcel_id_definition = models.TextField()

    #URL of the publishing municipality's website
    municipality_url = models.CharField(max_length=100, blank=True)

    #Email address of the person to contact regarding invalid data in this feed
    contact_email = models.CharField(max_length=100, blank=True)

class Source(models.Model):
    """
    Where something came from...
    Options include a Person, or a Feed

    This is a central place to tie together all of the different origins
    so we can always reference one object type
    """
    feed = models.ForeignKey(FeedInfo, blank=True)
    person = models.ForeignKey(Person, blank=True)
    #will this ultimately just be a Person though?
    #manager = models.ForeignKey(Manager, blank=True)

