from django import template
register = template.Library()

@register.filter('widget_type')
def widget_type(form_field_obj):
    """
    helper for templates to determine type
    and do specialized rendering in the template based on type
    
    http://stackoverflow.com/questions/1809874/get-type-of-django-form-widget-from-within-template
    """
    return form_field_obj.field.widget.__class__.__name__
    #return form_field_obj.field.__class__.__name__

