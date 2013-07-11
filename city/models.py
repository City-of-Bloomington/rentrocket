from django.db import models


#feed info moved to source.models.FeedInfo

class City(models.Model):
    """
    Details to define a specific City
    """
    name = models.CharField(max_length=200)

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')
