import re

def to_tag(item):
    """
    take any string and convert it to an acceptable tag

    tags should not contain spaces or special characters
    numbers, lowercase letters only
    underscores can be used, but they will be converted to spaces in some cases
    """
    item = item.lower()
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


def from_tag(item):
    """
    take any tag and attempt to convert it back...
    won't work with ' or /    
    """
    item = re.sub('_', ' ', item)
    return item

