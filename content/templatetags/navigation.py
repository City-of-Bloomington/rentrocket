from django import template

#from city.models import City, to_tag, all_cities
#from city.models import all_cities
from city.views import CitySelectForm, make_city_options

register = template.Library()

#https://docs.djangoproject.com/en/dev/topics/forms/
#https://docs.djangoproject.com/en/dev/ref/forms/fields/#choicefield
def make_nav(context):
    """
    this is meant to be called on every request
    determine if we know the current location or not
    then generate the navigation accordingly
    """

    #print dir(context)
    request = context['request']
    
    stored = request.session.get('city', default=None)

    #print "Stored city: %s" % stored
    #list of tuples: (link, content)
    #nav_items = [ ('/', "Home") ]
    nav_items = [ ]

    #select_form = CitySelectForm()

    if stored:
        #show any navigation items that are city specific
        #nav_items.append( ('/building/%s' % stored['tag'], "Map") )
        #nav_items.append( ('/city/resources/%s' % stored['tag'], "Resources") )
        nav_items.append( ('/city/%s' % stored['tag'], "Map") )
        nav_items.append( ('/city/%s/resources' % stored['tag'], "Resources") )

        #select_form.fields['choice'].initial = stored['tag']
    else:
        nav_items.append( ('/city/', "Map") )

    nav_items.append( ('/share/', "Share Data") )

    #nav_items.append( ('/partner/', "Partner With Us") )
        
    # for showing about in the navigation:
    #nav_items.append( ('/about', "About") )

    ## t = loader.get_template('navigation.html')
    ## c = Context({'items': nav_items, 'form': select_form})
    ## return t.render(c)

    return { 'items': nav_items, 'user': request.user }

register.inclusion_tag('navigation.html', takes_context=True)(make_nav)


def make_city_select(context):
    """
    """

    request = context['request']    
    stored = request.session.get('city', default=None)

    #old way, using select field for form:
    ## select_form = CitySelectForm()

    ## if stored:
    ##     select_form.fields['choice'].initial = stored['tag']

    initial = ''
    if stored:
        initial = stored['tag']

    select_form = CitySelectForm()

    options = make_city_options()

    return { 'form': select_form, 'options': options, 'initial': initial }

register.inclusion_tag('city_select.html', takes_context=True)(make_city_select)
