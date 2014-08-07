import json

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, redirect
from django import forms

from models import City, to_tag, all_cities
from resource_data import resource_data

class CitySelectForm(forms.Form):
    options = [ ('', "Choose location...") ]

    keys = all_cities.keys()
    keys.sort()
    for key in keys:
        options.append( (key, "%s, %s" % (all_cities[key]['name'], all_cities[key]['state'])) )


    options.append( ('other', "Other") )
    #http://stackoverflow.com/questions/2902008/django-how-do-i-add-arbitrary-html-attributes-to-input-fields-on-a-form
    #https://docs.djangoproject.com/en/dev/ref/forms/widgets/#select
    choice = forms.ChoiceField(options, widget=forms.Select(attrs={'onchange':"this.form.submit()"}))

#from django.shortcuts import render_to_response, get_object_or_404

#render vs render_to_response:
#http://stackoverflow.com/questions/5154358/django-what-is-the-difference-between-render-render-to-response-and-direc
#
# render() automatically includes context_instance (current request) with call

def change(request, city_tag=None):
    if request.method == 'POST': # If the form has been submitted...
        form = CitySelectForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            # ...
            #return HttpResponseRedirect('/thanks/') # Redirect after POST
            city_tag = form.cleaned_data['choice']

    if city_tag == "other":
        context = {'city': None, 'result':"Adding a new city..."}
        return render(request, 'change_city.html', context )

    else:
        #city = City.objects.filter(tag=city_tag)
        city = all_cities.get(city_tag, None)

        #result = ""
        if city:
            #result += "Found match: %s" % city[0].name
            #result += "Found match: %s" % city['name']

            #update the city in our session for future reference:
            request.session['city'] = city
            assert city['tag'] == city_tag
        else:
            #result += "No match found!"
            pass
        
        #look latest city up from session (either just set, or previously):
        stored = request.session.get('city', None)
        if stored:
            url = "/city/%s" % stored['tag']
            return redirect(url)

        else:
            context = {'city': city, 'result':"Unknown option..."}
            return render(request, 'change_city.html', context )

def resources(request, city_tag):
    city = all_cities.get(city_tag, None)

    #result = ""
    if city:
        #result += "Found match: %s" % city[0].name
        result = "<h2>%s, %s Resources:</h2>" % (city['name'], city['state'])
        if resource_data.has_key(city['tag']):
            result += resource_data[city['tag']]

        context = {'city': city, 'result':result}
        return render(request, 'resources.html', context )
    else:
        url = "/city/new" 
        return redirect(url)
        
def city_map(request, city_tag="bloomington_in"):
    #city = City.objects.filter(tag=city_tag)
    city = all_cities.get(city_tag, None)

    #default
    zoom = 14
    
    if not city:
        url = "/city/new"
        return redirect(url)
    else:
        context = {'lat': city['lat'],
                   'lng': city['lng'],
                   'zoom': zoom,
                   'city_tag': city_tag,
                   }

        return render(request, 'map.html', context )

def new_city(request):
    """
    show information about what is involved with adding a new city here:
    """
    context = {'result':"New city..."}
    return render(request, 'change_city.html', context )

def city(request, city_tag="bloomington_in"):
    city = City.objects.filter(tag=city_tag)

    result = ""
    if city:
        result += "Found match: %s" % city[0].name
    else:
        result += "No match found!"
        
    context = {'city': city, 'result':result}

    return render(request, 'city.html', context )

