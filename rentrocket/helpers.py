import re

from django.core import exceptions
from django.db import models
from django import forms
from django.utils.text import capfirst
from south.modelsinspector import add_introspection_rules

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

