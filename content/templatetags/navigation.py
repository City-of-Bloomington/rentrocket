from django import template

#from city.models import City, to_tag, all_cities
from city.models import all_cities
from city.views import CitySelectForm

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

    select_form = CitySelectForm()

    if stored:
        #show any navigation items that are city specific
        nav_items.append( ('/building/%s' % stored['tag'], "Map") )
        nav_items.append( ('/city/resources/%s' % stored['tag'], "Resources") )

        select_form.fields['choice'].initial = stored['tag']
    

    nav_items.append( ('/about', "About") )

    ## t = loader.get_template('navigation.html')
    ## c = Context({'items': nav_items, 'form': select_form})
    ## return t.render(c)

    return { 'items': nav_items, 'form': select_form }

register.inclusion_tag('navigation.html', takes_context=True)(make_nav)
