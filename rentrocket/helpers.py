import re

from django.core import exceptions
from django.db import models
from django import forms
from django.utils.text import capfirst
from south.modelsinspector import add_introspection_rules

from geopy import geocoders

def check_result(result):
    """
    do some common checks on any matches returned by address_search()
    
    update result in place
    """
    error = None
    #print result['place']
    parts = result['place'].split(',')
    
    #make sure we're in the US for now...
    #not set up to handle other cities yet.
    if (parts[-1].strip() != 'USA') and (parts[-1].strip() != 'United States'):
        error = "Cannot process addresses outside of the U.S. at this time"
    elif len(parts) < 3:
        error = "Could not find the city name: %s" % result['place']
    else:
        #processing moved to handle place
        pass
    #can have more than 4 parts returned,
    #eg street, University of Michigan, Law Quadrangle, etc
    #elif len(parts) <= 4:    
    #elif len(parts) > 4:
    #    error = "Too many parts found for address result: %s" % (parts)
        
    #print city_name, city_state, city_tag
    return error

def handle_place(matches, place, lat, lng, unit):
    """
    helper for adding unit in to results from lookup

    add unit back in everywhere, if found    
    """
    result = {'place': place, 'lat': lat, 'lng': lng}
    error = check_result(result)
    if not error:
        print "PLACE: ", place
        parts = place.split(',')
        #3 or 4 + (city or address)... this is something we can work with
        if len(parts) > 3:
            street = parts[0].strip()

            result['street'] = street

            if unit:
                street_total = result['street'] + ' ' + unit
                result['unit'] = unit
                result['street_total'] = street_total
                parts[0] = street_total
                result['place_total'] = ','.join(parts)
            else:
                result['street_total'] = result['street']
                result['place_total'] = result['place']
                

        if len(parts) > 2:
            result['city'] = parts[-3].strip()

            zipcode = ''
            state = ''
            #if a zipcode was matched, it will be in this part: , IN 47408,
            state_zip = parts[-2].strip()
            print "STATE_ZIP: ", state_zip
            if len(state_zip) == 2:
                state = state_zip
            elif state_zip:
                parts = state_zip.split()
                if len(parts) == 2:
                    (state, zipcode) = parts

            result['state'] = state
            result['zipcode'] = zipcode

        matches.append(result)

def address_search(query):
    error = None
    building = None
    search_options = []
    unit = ''
    matches = []

    if query:
        #before searching for the normalized address
        #check if there is a unit or apartment in the string
        #Google seems to have difficulty with different unit and apartment strings
        #especially if they are not numbers
        #https://code.google.com/p/gmaps-api-issues/issues/detail?id=5587

        #rentrocket/scripts 
        #python columbia-find_apartment_keys.py
        #[u'APT', u'UNIT', u'HOUSE', u'RM', u'HM', u'BLDG', u'LOT', u'TRLR', u'STE', u'SPK', u'DUP', u'ROOM', u'SUITE', u'HM1', u'OFC', u'GAR', u'HMRM', u'SHOP']
        units = ['unit', 'apartment', 'apt', 'suite', 'ste', 'trlr', 'trailer', 'room', 'rm']
        substitutes = { 'unit':'Unit', 'apartment':'Apt', 'apt':'Apt', 'suite':"Ste", 'ste':"Ste", 'trlr':"Trlr", 'trailer':"Trlr", 'room':"Rm", 'rm':"Rm" }

        for item in units:
            search = '(.+)( %s )(.+)' % item
            print "looking for ", search
            print "in: ", query
            match = re.search(search, query, re.I)
            if match:
                #now have 3 parts... find the corresponding unit number
                parts = match.group(3).split()
                unit_num = parts.pop(0)
                unit_num = unit_num.replace(',', '')
                unit_num = unit_num.strip()
                unit = substitutes[item] + ' ' + unit_num
                #print unit
                city_state = ' '.join(parts)

                query = match.group(1) + ', ' + city_state
                #print query

                #print match
                #print dir(match)            
                #for group in match.groups():
                #    print group
                #print match.groups()

        #the above will not match the google format of #xxx
        all_parts = query.split(',')
        street = all_parts[0]
        street_parts = street.split()
        last_part = street_parts[-1]
        if re.search('#', last_part):
            if unit:
                error = "Found multiple Unit identifiers. Please fix: %s, %s" % (unit, last_part)
            else:
                #matched a unit in the address
                #take care of splitting and merging these
                street, unit = street.split('#')
                unit = '#' + unit

                ## #see if we already matched a unit# earlier
                ## if result.has_key('unit'):
                ##     (prefix, suffix) = result['unit'].split()
                ##     if str(suffix) != str(unit):
                ##         error = "Found multiple unit options: %s, %s" % (result['unit'], unit)
                ##     #otherwise we can stick with the previous version

                ## else:
                ##     result['unit'] = unit
                ## print unit

        if not error:            
            google = geocoders.GoogleV3()

            options = google.geocode(query, exactly_one=False)
            if options:
                if isinstance(options[0], unicode):
                    #must only have one... different format:
                    (place, (lat, lng)) = options
                    handle_place(matches, place, lat, lng, unit)
                else:
                    for place, (lat, lng) in options:
                        handle_place(matches, place, lat, lng, unit)

    return matches, error, unit

#via: https://djangosnippets.org/snippets/1200/
#http://stackoverflow.com/questions/2726476/django-multiple-choice-field-checkbox-select-multiple
class MultiSelectFormField(forms.MultipleChoiceField):
    widget = forms.CheckboxSelectMultiple
    
    def __init__(self, *args, **kwargs):
        self.max_choices = kwargs.pop('max_choices', 0)
        #this didn't have an effect
        #kwargs['widget'] = forms.CheckboxSelectMultiple(choices=kwargs.get('choices', []))
        super(MultiSelectFormField, self).__init__(*args, **kwargs)

    def clean(self, value):
        if not value and self.required:
            raise forms.ValidationError(self.error_messages['required'])
        if value and self.max_choices and len(value) > self.max_choices:
            raise forms.ValidationError('You must select a maximum of %s choice%s.'
                    % (apnumber(self.max_choices), pluralize(self.max_choices)))
        return value


class MultiSelectField(models.Field):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def get_choices_default(self):
        return self.get_choices(include_blank=False)

    def validate(self, value, model_instance):
        arr_choices = self.get_choices_selected(self.get_choices_default())
        for opt_select in value:
            if (opt_select not in arr_choices): 
                raise exceptions.ValidationError(self.error_messages['invalid_choice'] % value)    
        return

    def get_choices_selected(self, arr_choices=''):
        if not arr_choices:
            return False
        list = []
        for choice_selected in arr_choices:
            list.append(choice_selected[0])
        return list
    
    def _get_FIELD_display(self, field):
        value = getattr(self, field.attname)
        choicedict = dict(field.choices)

    def formfield(self, **kwargs):
        # don't call super, as that overrides default widget if it has choices
        defaults = {'required': not self.blank, 'label': capfirst(self.verbose_name), 
                    'help_text': self.help_text, 'choices':self.choices}
        if self.has_default():
            defaults['initial'] = self.get_default()
        defaults.update(kwargs)
        return MultiSelectFormField(**defaults)

    #def get_db_prep_value(self, value, connection, prepared=False):
    def get_prep_value(self, value):
        if isinstance(value, basestring):
            return value
        elif isinstance(value, list):
            return ",".join(value)

    def value_to_string(self, obj):
        value = self._get_val_from_obj(obj)
        return self.get_prep_value(value)

    def to_python(self, value):
        if isinstance(value, list):
            return value
        return value.split(",")

    def contribute_to_class(self, cls, name):
        super(MultiSelectField, self).contribute_to_class(cls, name)
        if self.choices:
            func = lambda self, fieldname = name, choicedict = dict(self.choices):",".join([choicedict.get(value,value) for value in getattr(self,fieldname)])
            setattr(cls, 'get_%s_display' % self.name, func)


#add_introspection_rules([], ["^myapp\.stuff\.fields\.SomeNewField"])
add_introspection_rules([], ["^rentrocket\.helpers\.MultiSelectField"])
            
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

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
    item = re.sub("#", '', item)
    
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

