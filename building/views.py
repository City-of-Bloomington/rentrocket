import json, re

from django.template import Context, loader
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import login_required
from django.forms import ModelForm, extras, widgets
from django import forms

from django.contrib import messages
from django.core.urlresolvers import reverse

from models import Building, Unit, Listing, BuildingPerson, ChangeDetails

from city.models import City, to_tag, all_cities
from rentrocket.helpers import get_client_ip

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

    return render(request, 'index.html', context )

    #return HttpResponse("Hello, world. You're at the building index.")

def send_json(request, bldg_tag, city_tag):
    pass

def update(request, bldg_tag, city_tag):
    pass


class BuildingForm(ModelForm):
    class Meta:
        model = Building
        #fields = ['pub_date', 'headline', 'content', 'reporter']
        fields = [ 'name', 'website', 'type', 'sqft',
                   #'number_of_units', 'built_year', 'value',
                   
                   'who_pays_electricity', 'who_pays_gas', 'who_pays_water', 'who_pays_trash', 'who_pays_internet', 'who_pays_cable',


                   #TODO:
                   #even this should be calculated from the unit details
                   #'average_electricity', 'average_gas', 'average_water', 'average_trash',


                   #TODO:
                   #these can be calculated
                   #'total_average',
                   #only gas and electric included here:
                   #(use this / sqft for energy score)
                   #'energy_average',

                   #this is a temporary field until score is
                   #calculated automatically
                   
                   #regardless of who pays utilities, 
                   #once we have energy data,
                   #we will want to summarize the results here
                   #so that we can use this to color code appropriately
                   'energy_score',

                   #these will usually happen on a building level

                   'heat_source_details',
                   'heat_source_other',

                   #'energy_saving_features',
                   'energy_saving_details',
                   'energy_saving_other',

                   #'renewable_energy',
                   'renewable_energy_details',
                   'renewable_energy_other',


                   #smart living
                   #make a separate field
                   'composting',
                   'recycling',

                   #'garden',
                   'garden_details',
                   'garden_other',

                   #'bike_friendly',
                   'bike_friendly_details',
                   'bike_friendly_other',

                   #'walk_friendly',
                   'walk_friendly_details',
                   'walk_friendly_other',

                   'transit_friendly_details',
                   'transit_friendly_other',

                   'smart_living',

                                      
                   #amenities
                   'air_conditioning',

                   'laundry',

                   'parking_options',

                   #generally, are pets allowed?
                   #details for this should go in lease
                   #pets = models.BooleanField(default=False)
                   #'pets',

                   #switching to string to allow description:
                   'pets_options',
                   'pets_other',

                   'gym',
                   'pool',
                   'game_room',
                   #for everything else...
                   #anything here will not be available as a filter...
                   #if there is a common addition that should be part of filter,
                   #make a separate field
                   'amenities'

                   ]
        YES_OR_NO = (
            (True, 'Yes'),
            (False, 'No')
            )
        
        widgets = {
            'renewable_energy': forms.RadioSelect(choices=YES_OR_NO, attrs={'class': 'yesno'}),
            'composting': forms.RadioSelect(choices=YES_OR_NO),
            'recycling': forms.RadioSelect(choices=YES_OR_NO),
            'garden': forms.RadioSelect(choices=YES_OR_NO),
            'bike_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'walk_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'transit_friendly': forms.RadioSelect(choices=YES_OR_NO),
            'air_conditioning': forms.RadioSelect(choices=YES_OR_NO),
            'gym': forms.RadioSelect(choices=YES_OR_NO),
            'pool': forms.RadioSelect(choices=YES_OR_NO),
            'game_room': forms.RadioSelect(choices=YES_OR_NO),
            
        }
                   




@login_required
def edit(request, bldg_tag, city_tag):
    city = City.objects.filter(tag=city_tag)
    buildings = Building.objects.filter(city=city).filter(tag=bldg_tag)
    if buildings.count():
        building = buildings[0]

    else:
        building = None

    if request.method == 'POST':
        form = BuildingForm(request.POST, instance=building)

        if form.is_valid(): # All validation rules pass
            updated = form.save(commit=False)

            #update any summary boolean fields here
            #(this should help with searching)
            if updated.energy_saving_details or updated.energy_saving_other :
                updated.energy_saving_features = True
            else:
                updated.energy_saving_features  = False
            
            if updated.renewable_energy_details or updated.renewable_energy_other :
                updated.renewable_energy = True
            else:
                updated.renewable_energy = False
            
            if updated.garden_details or updated.garden_other:
                updated.garden = True
            else:
                updated.garden = False
            
            if updated.bike_friendly_details or updated.bike_friendly_other :
                updated.bike_friendly = True
            else:
                updated.bike_friendly = False
            
            if updated.walk_friendly_details or updated.walk_friendly_other :
                updated.walk_friendly = True
            else:
                updated.walk_friendly = False
            
            if updated.transit_friendly_details or updated.transit_friendly_other :
                updated.transit_friendly = True
            else:
                updated.transit_friendly = False
            
            if updated.parking_options:
                updated.parking = True
            else:
                updated.parking = False
            
            if updated.pets_options or updated.pets_other :
                updated.pets = True
            else:
                updated.pets = False

            print json.dumps(updated.diff)
            
            #print updated.diff
            changes = ChangeDetails()
            changes.ip_address = get_client_ip(request)
            changes.user = request.user
            changes.diffs = json.dumps(updated.diff)
            changes.building = updated
            #not required
            #changes.unit =
            changes.save()
            
            #now it's ok to save the building details:
            updated.save()

            #redirect to building details with an edit message
            messages.add_message(request, messages.INFO, 'Saved changes to building.')
            finished_url = reverse('building.views.details', args=(updated.tag, updated.city.tag))
            
            return redirect(finished_url)
    else:
        form = BuildingForm(instance=building)
        
    context = { 'building': building,
                'user': request.user,
                'form': form,

                }
    return render(request, 'building-edit.html', context)

def details(request, bldg_tag, city_tag):
    city = City.objects.filter(tag=city_tag)
    #old way... this doesn't work very reliably:
    #address = re.sub('_', ' ', bldg_tag)
    #buildings = Building.objects.filter(city=city).filter(address=address)
    buildings = Building.objects.filter(city=city).filter(tag=bldg_tag)
    if buildings.count():
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
            # don't want to set this unless it's different:
            #unit.address = building.address 

            ## bedrooms
            ## bathrooms
            ## sqft
            ## max_occupants
            unit.save()
    else:
        building = None
        
    context = { 'building': building,
                'user': request.user,
                'redirect_field': REDIRECT_FIELD_NAME,
                }
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

