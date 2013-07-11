from django.db import models

class Person(models.Model):
    """
    this should be replaced with Authentication models
    """
    name = models.CharField(max_length=20)
    
