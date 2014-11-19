from django.db import models
from city.models import City

class Person(models.Model):
    """
    this should be replaced or associated with Authentication models
    """
    name = models.CharField(max_length=200)

    address = models.CharField(max_length=200, blank=True)

    #may not have a city
    city = models.ForeignKey(City, blank=True, null=True)

    #latitude = models.FloatField()
    #longitude = models.FloatField()

    email = models.CharField(max_length=200, blank=True)

    #especially useful for property managers
    website = models.CharField(max_length=200, blank=True)

    phone = models.CharField(max_length=20, default='', blank=True)
