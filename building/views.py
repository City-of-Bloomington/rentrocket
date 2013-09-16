import json

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render

from models import Building, Unit, Listing

from city.models import City, to_tag

#from django.shortcuts import render_to_response, get_object_or_404

#render vs render_to_response:
#http://stackoverflow.com/questions/5154358/django-what-is-the-difference-between-render-render-to-response-and-direc
#
# render() automatically includes context_instance (current request) with call

def index(request):
    ## t = loader.get_template('index.html')
    ## t = loader.get_template('preferences/index.html')
    ## c = Context({
    ##     'latest_preferences': latest_preferences,
    ## })
    ## return HttpResponse(t.render(c))

    ## form = EventForm()
    
    ## #render_to_response does what above (commented) section does
    ## #return render_to_response('general/index.html', {'user': request.user})

    #buildings = Building.objects.all().order_by('-pub_date')[:5]
    #buildings = Building.objects.all()

    city = City.objects.filter(tag=to_tag("Ann Arbor"))
    
    buildings = Building.objects.filter(city=city)
    context = {'buildings': buildings}
#    return render(request, 'polls/index.html', context)

    return render(request, 'index.html', context )

    #return HttpResponse("Hello, world. You're at the building index.")


def map(request, lat=39.166537, lng=-86.531754, zoom=14):
    
    #buildings = Building.objects.filter(city=city)
    context = {'lat': lat,
               'lng': lng,
               'zoom': zoom,
               }

    return render(request, 'map.html', context )

def lookup(request, lat1, lng1, lat2, lng2, type="rental", limit=100):
    """
    this is a json request to lookup buildings within a given area
    should return json results that are easy to parse and show on a map

    http://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    """
    
    bq = Building.objects.all().filter(latitude__gte=float(lat1)).filter(longitude__gte=float(lng1)).filter(latitude__lte=float(lat2)).filter(longitude__lte=float(lng2))
    all_bldgs = []
    for building in bq[:limit]:
        all_bldgs.append(building.to_dict())
        
    bldg_dict = {'buildings': all_bldgs, 'total': len(bq)}

    #print bldg_dict
    
    return HttpResponse(json.dumps(bldg_dict), content_type="application/json")

