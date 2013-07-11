from django.db import models


#feed info moved to source.models.FeedInfo

class City(models.Model):
    """
    Details to define a specific City
    """
    name = models.CharField(max_length=200)
    #this is what we'll use to look up a city:
    #tag = models.CharField(max_length=200, unique=True)

    added = models.DateTimeField('date published')
    updated = models.DateTimeField('date updated')

    def to_tag(self):
        """
        take any string and convert it to an acceptable tag

        tags should not contain spaces or special characters
        numbers, lowercase letters only
        underscores can be used, but they will be converted to spaces in some cases
        """
        item = self.name.lower()
        #get rid of trailing and leading blank spaces:
        item = item.strip()
        item = re.sub(' ', '_', item)
        item = re.sub("/", '_', item)
        item = re.sub("\\\\'", '', item)
        item = re.sub("\\'", '', item)
        item = re.sub("'", '', item)

        #todo:
        # filter any non alphanumeric characters

        return item
