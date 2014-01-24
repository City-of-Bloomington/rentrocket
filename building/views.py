import json, re

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, redirect

from models import Building, Unit, Listing, BuildingPerson

from city.models import City, to_tag, all_cities

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

def update(request, bldg_tag, city_tag):
    pass
 
def edit(request, bldg_tag, city_tag):
    pass

def send_json(request, bldg_tag, city_tag):
    pass

def details(request, bldg_tag, city_tag):
    city = City.objects.filter(tag=city_tag)    
    address = re.sub('_', ' ', bldg_tag)
    buildings = Building.objects.filter(city=city).filter(address=address)
    building = buildings[0]
    
    if not building.units.count():
        #must have a building with no associated units...
        #may only have one unit
        #or others may have been incorrectly created as separate buildings
        #either way we can start by making a new unit here
        #(and then merging in any others manually)

        unit = Unit()
        unit.building = building
        unit.number = ''
        unit.address = building.address 

        ## bedrooms
        ## bathrooms
        ## sqft
        ## max_occupants
        unit.save()
        
    context = { 'building': building }
    return render(request, 'details.html', context)

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

